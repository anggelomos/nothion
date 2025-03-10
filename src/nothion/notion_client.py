from datetime import datetime, timedelta
from typing import List, Optional

from tickthon import Task, ExpenseLog

from nothion import PersonalStats
from nothion._config import NT_TASKS_DB_ID, NT_STATS_DB_ID, NT_NOTES_DB_ID, NT_EXPENSES_DB_ID
from nothion._notion_payloads import NotionPayloads
from nothion._notion_table_headers import TasksHeaders, StatsHeaders
from nothion._notion_api import NotionAPI


class NotionClient:

    def __init__(self,
                 auth_secret: str,
                 tasks_db_id: str | None = None,
                 stats_db_id: str | None = None,
                 notes_db_id: str | None = None,
                 expenses_db_id: str | None = None):
        self.notion_api = NotionAPI(auth_secret)
        self.active_tasks: List[Task] = []

        # Use provided database IDs or fall back to config defaults
        self.tasks_db_id = tasks_db_id or NT_TASKS_DB_ID
        self.stats_db_id = stats_db_id or NT_STATS_DB_ID
        self.notes_db_id = notes_db_id or NT_NOTES_DB_ID
        self.expenses_db_id = expenses_db_id or NT_EXPENSES_DB_ID

        # Initialize NotionPayloads with database IDs
        self.notion_payloads = NotionPayloads(
            tasks_db_id=self.tasks_db_id,
            stats_db_id=self.stats_db_id,
            notes_db_id=self.notes_db_id,
            expenses_db_id=self.expenses_db_id
        )

        # Initialize inner handlers without redundant database IDs
        self.tasks = self.TasksHandler(self)
        self.notes = self.NotesHandler(self)
        self.stats = self.StatsHandler(self)
        self.expenses = self.ExpensesHandler(self)
        self.blocks = self.BlocksHandler(self)

    @staticmethod
    def _parse_notion_tasks(raw_tasks: List[dict] | dict) -> List[Task]:
        """Parses the raw tasks from Notion into Task objects."""

        if not isinstance(raw_tasks, list):
            raw_tasks = [raw_tasks]

        parsed_tasks = []
        for raw_task in raw_tasks:
            task_properties = raw_task["properties"]

            timezone = ""
            if task_properties[TasksHeaders.TIMEZONE.value]["rich_text"]:
                timezone = task_properties[TasksHeaders.TIMEZONE.value]["rich_text"][0]["plain_text"]

            due_date = ""
            if task_properties[TasksHeaders.DUE_DATE.value]["date"]:
                due_date = task_properties[TasksHeaders.DUE_DATE.value]["date"]["start"]

            created_date = ""
            if task_properties[TasksHeaders.CREATED_DATE.value]["date"]:
                created_date = task_properties[TasksHeaders.CREATED_DATE.value]["date"]["start"]

            project_id = ""
            if task_properties[TasksHeaders.PROJECT_ID.value]["rich_text"]:
                project_id = task_properties[TasksHeaders.PROJECT_ID.value]["rich_text"][0]["plain_text"]

            column_id = ""
            if task_properties[TasksHeaders.COLUMN_ID.value]["rich_text"]:
                column_id = task_properties[TasksHeaders.COLUMN_ID.value]["rich_text"][0]["plain_text"]

            parsed_tasks.append(Task(title=task_properties[TasksHeaders.NOTE.value]["title"][0]["plain_text"],
                                     status=2 if task_properties[TasksHeaders.DONE.value]["checkbox"] else 0,
                                     ticktick_id=task_properties[TasksHeaders.TICKTICK_ID.value]
                                     ["rich_text"][0]["plain_text"],
                                     column_id=column_id,
                                     ticktick_etag=task_properties[TasksHeaders.TICKTICK_ETAG.value]
                                     ["rich_text"][0]["plain_text"],
                                     created_date=created_date,
                                     focus_time=task_properties[TasksHeaders.FOCUS_TIME.value]["number"],
                                     deleted=int(raw_task["archived"]),
                                     tags=tuple([tag["name"] for tag in task_properties[TasksHeaders.TAGS.value]
                                                                                       ["multi_select"]]),
                                     project_id=project_id,
                                     timezone=timezone,
                                     due_date=due_date))

        return parsed_tasks

    # Main class for task-related operations
    class TasksHandler:
        def __init__(self, client):
            self.client = client

        def get_active_tasks(self) -> List[Task]:
            """Gets all active tasks from Notion that are not done."""
            payload = self.client.notion_payloads.get_active_tasks()
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)
            notion_tasks = self.client._parse_notion_tasks(raw_tasks)
            self.client.active_tasks = notion_tasks
            return notion_tasks

        def get_notion_task(self, ticktick_task: Task) -> Optional[Task]:
            """Gets the task from Notion that have the given ticktick etag."""
            payload = self.client.notion_payloads.get_notion_task(ticktick_task)
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)

            notion_tasks = self.client._parse_notion_tasks(raw_tasks)
            if notion_tasks:
                return notion_tasks[0]
            return None

        def get_notion_id(self, ticktick_task: Task) -> str:
            """Gets the Notion ID of a task."""
            payload = self.client.notion_payloads.get_notion_task(ticktick_task)
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)

            return raw_tasks[0]["id"].replace("-", "")

        def is_already_created(self, task: Task) -> bool:
            """Checks if a task is already created in Notion."""
            payload = self.client.notion_payloads.get_notion_task(task)
            raw_tasks = self.client.notion_api.query_table(self.client.tasks_db_id, payload)
            return len(raw_tasks) > 0

        def create(self, task: Task) -> Optional[dict]:
            """Creates a task in Notion."""
            payload = self.client.notion_payloads.create_task(task)

            if not self.is_already_created(task):
                return self.client.notion_api.create_table_entry(payload)
            return None

        def update(self, task: Task):
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

    # Notes-related operations
    class NotesHandler:
        def __init__(self, client):
            self.client = client

        def get_task_note(self, ticktick_task: Task) -> Optional[Task]:
            """Gets the task from Notion's notes database that have the given ticktick etag."""
            payload = self.client.notion_payloads.get_notion_task(ticktick_task)
            raw_tasks = self.client.notion_api.query_table(self.client.notes_db_id, payload)

            notion_tasks = self.client._parse_notion_tasks(raw_tasks)
            if notion_tasks:
                return notion_tasks[0]
            return None

        def get_notion_id(self, ticktick_task: Task) -> str:
            """Gets the Notion ID of a task note."""
            payload = self.client.notion_payloads.get_notion_task(ticktick_task)
            raw_tasks = self.client.notion_api.query_table(self.client.notes_db_id, payload)

            return raw_tasks[0]["id"].replace("-", "")

        def is_task_already_created(self, task: Task) -> bool:
            """Checks if a task note is already created in Notion."""
            payload = self.client.notion_payloads.get_notion_task(task)
            raw_tasks = self.client.notion_api.query_table(self.client.notes_db_id, payload)
            return len(raw_tasks) > 0

        def create_task(self, task: Task) -> Optional[dict]:
            """Creates a task in the notes database in Notion."""
            payload = self.client.notion_payloads.create_task_note(task)

            if not self.is_task_already_created(task):
                return self.client.notion_api.create_table_entry(payload)
            return None

        def update_task(self, task: Task):
            """Updates a task note in Notion."""
            page_id = self.get_notion_id(task)

            notion_task = self.client.tasks.get_notion_task(task)
            is_task_unprocessed = False
            if notion_task:
                is_task_unprocessed = "unprocessed" in notion_task.tags
            payload = self.client.notion_payloads.update_task_note(task, is_task_unprocessed)

            self.client.notion_api.update_table_entry(page_id, payload)

        def complete_task(self, task: Task):
            """Completes a task note in Notion."""
            page_id = self.get_notion_id(task)
            payload = self.client.notion_payloads.complete_task()
            self.client.notion_api.update_table_entry(page_id, payload)

        def delete_task(self, task: Task):
            """Deletes a task note from Notion."""
            task_payload = self.client.notion_payloads.get_notion_task(task)
            raw_tasks = self.client.notion_api.query_table(self.client.notes_db_id, task_payload)

            delete_payload = self.client.notion_payloads.delete_table_entry()
            for raw_task in raw_tasks:
                page_id = raw_task["id"]
                self.client.notion_api.update_table_entry(page_id, delete_payload)

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

        def is_highlight_log_already_created(self, task: Task) -> bool:
            """Checks if a highlight log is already created in Notion."""
            payload = self.client.notion_payloads.get_highlight_log(task)
            raw_tasks = self.client.notion_api.query_table(self.client.notes_db_id, payload)
            return len(raw_tasks) > 0

        def add_highlight_log(self, log: Task) -> dict | None:
            """Adds a highlight log to the Notes DB in Notion."""
            payload = self.client.notion_payloads.create_highlight_log(log)

            if not self.is_highlight_log_already_created(log):
                return self.client.notion_api.create_table_entry(payload)
            return None

        def get_daily_journal_data(self, date: datetime) -> dict:
            """"Gets the page data of a daily journal entry for a specific date."""
            journal_entry = self.client.notion_api.query_table(self.client.notes_db_id,
                                                               self.client.notion_payloads.get_daily_journal_entry(date)
                                                               )
            return journal_entry[0]

        def get_daily_journal_content(self, date: datetime) -> list:
            """Gets the content of a journal entry for a specific date."""
            journal_entry = self.get_daily_journal_data(date)["id"]
            return self.client.blocks.get_all_children(journal_entry)

    # Stats-related operations
    class StatsHandler:
        def __init__(self, client):
            self.client = client

        @staticmethod
        def _parse_stats_rows(rows: List[dict] | dict) -> List[PersonalStats]:
            """Parses the raw stats rows from Notion into PersonalStats objects."""
            if not isinstance(rows, List):
                rows = [rows]

            rows_parsed = []
            for row in rows:
                row_properties = row["properties"]
                rows_parsed.append(
                    PersonalStats(date=row_properties[StatsHeaders.DATE.value]["date"]["start"],
                                  weight=row_properties[StatsHeaders.WEIGHT.value]["number"] or 0,
                                  sleep_time=row_properties[StatsHeaders.SLEEP_TIME.value]["number"] or 0,
                                  work_time=row_properties[StatsHeaders.WORK_TIME.value]["number"] or 0,
                                  leisure_time=row_properties[StatsHeaders.LEISURE_TIME.value]["number"] or 0,
                                  focus_time=row_properties[StatsHeaders.FOCUS_TIME.value]["number"] or 0))
            return rows_parsed

        def _get_last_row_checked(self) -> Optional[PersonalStats]:
            """Gets the last checked row from the stats in Notion database."""
            checked_rows = self.client.notion_api.query_table(self.client.stats_db_id,
                                                              self.client.notion_payloads.get_checked_stats_rows())
            if checked_rows:
                return self._parse_stats_rows(checked_rows[-1])[0]
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

        def update(self, stat_data: PersonalStats):
            """Updates a row in the stats database in Notion."""
            date_row = self.client.notion_api.query_table(self.client.stats_db_id,
                                                          self.client.notion_payloads.get_date_rows(stat_data.date))

            if date_row:
                row_id = date_row[0]["id"]
                self.client.notion_api.update_table_entry(row_id,
                                                          self.client.notion_payloads.update_stats_row(stat_data,
                                                                                                       new_row=False))
            else:
                self.client.notion_api.create_table_entry(self.client.notion_payloads.update_stats_row(stat_data,
                                                                                                       new_row=True))

        def get_between_dates(self, start_date: datetime, end_date: datetime) -> List[PersonalStats]:
            """Gets stats between two dates."""
            raw_data = self.client.notion_api.query_table(self.client.stats_db_id,
                                                          self.client.notion_payloads.get_data_between_dates(start_date,
                                                                                                             end_date))
            return self._parse_stats_rows(raw_data)

    # Block-related operations
    class BlocksHandler:
        def __init__(self, client):
            self.client = client

        @staticmethod
        def _parse_block(block: dict) -> str:
            """Parses a block from Notion into a string."""
            block_type = block["type"]
            block_raw_text = block[block_type].get("rich_text", [])
            block_text = block_raw_text[0]["plain_text"] if block_raw_text else ""

            if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
                return block_text
            elif block_type == "bulleted_list_item":
                return "- " + block_text
            elif block_type == "toggle":
                return "> " + block_text
            return block_type

        def get_all_children(self, block_id: str) -> list:
            """Recursively gets the children of a block in Notion."""
            children = []
            children_data = self.client.notion_api.get_block_children(block_id)

            for child in children_data.get("results", []):
                parsed_child: list[str | list] = [self._parse_block(child)]
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
