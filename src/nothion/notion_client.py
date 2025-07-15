from datetime import datetime, timedelta
from typing import List, Optional

from tickthon import Task

from nothion import PersonalStats
from nothion._notion_parsers import NotionParsers
from nothion._notion_payloads import NotionPayloads
from nothion._notion_api import NotionAPI
from nothion.data_models.expense_log import ExpenseLog


class NotionClient:

    def __init__(self,
                 auth_secret: str,
                 tasks_db_id: str = "",
                 stats_db_id: str = "",
                 notes_db_id: str = "",
                 expenses_db_id: str = ""):
        self.notion_api = NotionAPI(auth_secret)
        self.active_tasks: List[Task] = []

        self.tasks_db_id = tasks_db_id
        self.stats_db_id = stats_db_id
        self.notes_db_id = notes_db_id
        self.expenses_db_id = expenses_db_id

        self.notion_payloads = NotionPayloads(
            tasks_db_id=self.tasks_db_id,
            stats_db_id=self.stats_db_id,
            notes_db_id=self.notes_db_id,
            expenses_db_id=self.expenses_db_id
        )

        self.tasks = self.TasksHandler(self)
        self.notes = self.NotesHandler(self)
        self.stats = self.StatsHandler(self)
        self.expenses = self.ExpensesHandler(self)
        self.blocks = self.BlocksHandler(self)

    class TasksHandler:
        def __init__(self, client):
            self.client = client

        def get_active_tasks(self) -> List[Task]:
            """Gets all active tasks from Notion that are not done."""
            payload = self.client.notion_payloads.get_active_tasks()
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)
            notion_tasks = NotionParsers.parse_notion_tasks(raw_tasks)
            self.client.active_tasks = notion_tasks
            return notion_tasks

        def get_task(self, ticktick_task: Task) -> Optional[Task]:
            """Gets the task from Notion that have the given ticktick etag."""
            payload = self.client.notion_payloads.get_notion_task(ticktick_task)
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)

            notion_tasks = NotionParsers.parse_notion_tasks(raw_tasks)
            if notion_tasks:
                return notion_tasks[0]
            return None

        def get_notion_id(self, ticktick_task: Task) -> str:
            """Gets the Notion ID of a task."""
            payload = self.client.notion_payloads.get_notion_task(ticktick_task)
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)

            return raw_tasks[0]["id"].replace("-", "")

        def is_task_already_created(self, task: Task) -> bool:
            """Checks if a task is already created in Notion."""
            payload = self.client.notion_payloads.get_notion_task(task)
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)
            return len(raw_tasks) > 0

        def create(self, task: Task) -> Optional[dict]:
            """Creates a task in Notion."""
            payload = self.client.notion_payloads.create_task(task)

            if not self.is_task_already_created(task):
                return self.client.notion_api.create_table_entry(payload)
            return None

        def update_task(self, task: Task):
            """Updates a task in Notion."""
            page_id = self.get_notion_id(task)
            payload = self.client.notion_payloads.update_task(task)
            self.client.notion_api.update_table_entry(page_id, payload)

        def complete(self, task: Task):
            """Completes a task in Notion."""
            page_id = self.get_notion_id(task)
            payload = self.client.notion_payloads.complete_task()
            self.client.notion_api.update_table_entry(page_id, payload)

        def delete(self, task: Task):
            """Deletes a task from Notion."""
            task_payload = self.client.notion_payloads.get_notion_task(task)
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, task_payload)

            delete_payload = self.client.notion_payloads.delete_table_entry()
            for raw_task in raw_tasks:
                page_id = raw_task["id"]
                self.client.notion_api.update_table_entry(page_id, delete_payload)

    class NotesHandler:
        def __init__(self, client):
            self.client = client

        def is_page_already_created(self, title: str, page_type: str) -> bool:
            """Checks if a note's page is already created in Notion."""
            payload = self.client.notion_payloads.get_note_page(title, page_type)
            raw_tasks = self.client.notion_api.query_table(self.client.notes_db_id, payload)
            return len(raw_tasks) > 0

        def create_page(self,
                        title: str,
                        page_type: str,
                        page_subtype: tuple[str],
                        date: datetime,
                        content: str) -> dict | None:
            """Creates a note page in Notion."""
            payload = self.client.notion_payloads.create_note_page(title, page_type, page_subtype, date, content)

            if not self.is_page_already_created(title, page_type):
                return self.client.notion_api.create_table_entry(payload)
            return None

    class StatsHandler:
        def __init__(self, client):
            self.client = client
            self.payloads = self.client.notion_payloads

        def _get_last_row_checked(self) -> Optional[PersonalStats]:
            """Gets the last checked row from the stats in Notion database."""
            checked_rows = self.client.notion_api.query_table(self.client.stats_db_id,
                                                              self.payloads.get_checked_stats_rows())

            if checked_rows:
                return NotionParsers.parse_stats_rows([checked_rows[-1]])[0]
            return None

        def get_incomplete_dates(self, limit_date: datetime) -> List[str]:
            """Gets the dates that are incomplete in the stats database."""
            initial_date = datetime(limit_date.year, 1, 1)
            last_checked_row = self._get_last_row_checked()
            if last_checked_row:
                current_date = datetime.strptime(last_checked_row.date, "%Y-%m-%d")
                initial_date = current_date - timedelta(days=14)

            dates = []
            delta = limit_date - initial_date
            for delta_days in range(delta.days + 1):
                day = initial_date + timedelta(days=delta_days)
                dates.append(day.strftime("%Y-%m-%d"))

            return dates

        def update(self, stat_data: PersonalStats, overwrite_stats: bool = False):
            """Updates a row in the stats database in Notion."""
            raw_date_row = self.client.notion_api.query_table(self.client.stats_db_id,
                                                              self.payloads.get_date_rows(stat_data.date))

            date_row = NotionParsers.parse_stats_rows(raw_date_row)

            if date_row:
                row_id = raw_date_row[0]["id"]
                self.client.notion_api.update_table_entry(row_id,
                                                          self.payloads.update_stats_row(stat_data,
                                                                                         old_stats=date_row,
                                                                                         overwrite_stats=overwrite_stats
                                                                                         ))
            else:
                self.client.notion_api.create_table_entry(self.payloads.update_stats_row(stat_data,
                                                                                         new_row=True))

        def get_between_dates(self, start_date: datetime, end_date: datetime) -> List[PersonalStats]:
            """Gets stats between two dates."""
            raw_data = self.client.notion_api.query_table(self.client.stats_db_id,
                                                          self.payloads.get_data_between_dates(start_date,
                                                                                               end_date))
            return NotionParsers.parse_stats_rows(raw_data)

    class BlocksHandler:
        def __init__(self, client):
            self.client = client

        def get_all_children(self, block_id: str) -> list:
            """Recursively gets the children of a block in Notion."""
            children = []
            children_data = self.client.notion_api.get_block_children(block_id)

            for child in children_data.get("results", []):
                parsed_child: list[str | list] = [NotionParsers.parse_block(child)]
                children.append(parsed_child)

                if child.get("has_children", False):
                    parsed_child.append(self.get_all_children(child["id"]))

            return children

    class ExpensesHandler:
        def __init__(self, client):
            self.client = client

        def add_expense_log(self, expense_log: ExpenseLog) -> dict:
            """Adds an expense log to the expenses DB in Notion."""
            payload = self.client.notion_payloads.create_expense_log(expense_log)
            return self.client.notion_api.create_table_entry(payload)
