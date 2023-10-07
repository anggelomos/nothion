import datetime
from typing import List, Optional

from . import PersonalStats
from ._config import NT_TASKS_DB_ID, NT_STATS_DB_ID
from ._notion_payloads import NotionPayloads
from ._notion_table_headers import TasksHeaders, StatsHeaders
from tickthon import Task

from ._notion_api import NotionAPI
from .expense_log_model import ExpenseLog
from .personal_stats_model import TimeStats


class NotionClient:

    def __init__(self, auth_secret: str):
        self.notion_api = NotionAPI(auth_secret)
        self.active_tasks: List[Task] = []

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

            project_id = ""
            if task_properties[TasksHeaders.PROJECT_ID.value]["rich_text"]:
                project_id = task_properties[TasksHeaders.PROJECT_ID.value]["rich_text"][0]["plain_text"]

            recurrent_id = ""
            if task_properties[TasksHeaders.RECURRENT_ID.value]["rich_text"]:
                recurrent_id = task_properties[TasksHeaders.RECURRENT_ID.value]["rich_text"][0]["plain_text"]

            parsed_tasks.append(Task(title=task_properties[TasksHeaders.TASK.value]["title"][0]["plain_text"],
                                     status=2 if task_properties[TasksHeaders.DONE.value]["checkbox"] else 0,
                                     ticktick_id=task_properties[TasksHeaders.TICKTICK_ID.value]
                                     ["rich_text"][0]["plain_text"],
                                     focus_time=task_properties[TasksHeaders.FOCUS_TIME.value]["number"],
                                     deleted=int(raw_task["archived"]),
                                     tags=[tag["name"] for tag in task_properties[TasksHeaders.TAGS.value]
                                     ["multi_select"]],
                                     project_id=project_id,
                                     timezone=timezone,
                                     due_date=due_date,
                                     recurrent_id=recurrent_id))

        return parsed_tasks

    def get_active_tasks(self) -> List[Task]:
        """Gets all active tasks from Notion that are not done."""
        payload = NotionPayloads.get_active_tasks()

        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)
        notion_tasks = self._parse_notion_tasks(raw_tasks)

        self.active_tasks = notion_tasks
        return notion_tasks

    def get_tasks_by_id(self, ticktick_id: str) -> List[Task]:
        """Gets all tasks from Notion that have the given ticktick id."""
        payload = NotionPayloads.get_task_by_id(ticktick_id)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)

        notion_tasks = self._parse_notion_tasks(raw_tasks)
        return notion_tasks

    def delete_task(self, ticktick_id: str):
        """Deletes a task from Notion."""
        task_payload = NotionPayloads.get_task_by_id(ticktick_id)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, task_payload)

        delete_payload = NotionPayloads.delete_table_entry()
        for raw_task in raw_tasks:
            page_id = raw_task["id"]
            self.notion_api.update_table_entry(page_id, delete_payload)

    def get_task_notion_id(self, ticktick_id: str) -> str:
        """Gets the Notion ID of a task."""
        payload = NotionPayloads.get_task_by_id(ticktick_id)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)

        return raw_tasks[0]["id"].replace("-", "")

    def is_task_already_created(self, ticktick_id: str, due_date: str = "") -> bool:
        """Checks if a task is already created in Notion."""
        payload = NotionPayloads.get_task_by_id(ticktick_id, due_date=due_date)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)
        return len(raw_tasks) > 0

    def create_task(self, task: Task) -> Optional[dict]:
        """Creates a task in Notion.

        Args:
            task: The task to create.

        Returns:
            The response from Notion if the task was created.
        """

        payload = NotionPayloads.create_task(task)

        if not self.is_task_already_created(task.ticktick_id, task.due_date):
            return self.notion_api.create_table_entry(payload)
        return None

    def update_task(self, task: Task):
        """Updates a task in Notion."""
        page_id = self.get_task_notion_id(task.ticktick_id)
        payload = NotionPayloads.update_task(task)
        self.notion_api.update_table_entry(page_id, payload)

    def add_expense_log(self, expense_log: ExpenseLog) -> dict:
        """Adds an expense log to the expenses DB in Notion."""
        payload = NotionPayloads.create_expense_log(expense_log)
        return self.notion_api.create_table_entry(payload)

    @staticmethod
    def _parse_stats_rows(rows: List[dict] | dict) -> List[PersonalStats]:
        """Parses the raw stats rows from Notion into PersonalStats objects."""
        if not isinstance(rows, List):
            rows = [rows]

        rows_parsed = []
        for row in rows:
            row_properties = row["properties"]
            time_stats = TimeStats(work_time=row_properties[StatsHeaders.WORK_TIME.value]["number"] or 0,
                                   leisure_time=row_properties[StatsHeaders.LEISURE_TIME.value]["number"] or 0,
                                   focus_time=row_properties[StatsHeaders.FOCUS_TIME.value]["number"] or 0)

            rows_parsed.append(PersonalStats(date=row_properties[StatsHeaders.DATE.value]["date"]["start"],
                                             weight=row_properties[StatsHeaders.WEIGHT.value]["number"] or 0,
                                             time_stats=time_stats))
        return rows_parsed

    def _get_last_checked(self) -> Optional[PersonalStats]:
        """Gets the last checked row from the stats in Notion database."""
        checked_rows = self.notion_api.query_table(NT_STATS_DB_ID, NotionPayloads.get_checked_stats_rows())
        if checked_rows:
            return self._parse_stats_rows(checked_rows[-1])[0]
        return None

    def get_incomplete_stats_dates(self, limit_date: datetime.date) -> List[str]:
        """Gets the dates that are incomplete in the stats database starting 14 days before the limit date.

        Args:
            limit_date: The limit date that is checked to get the incomplete dates.

        Returns:
            A list of dates in format YYYY-MM-DD.
        """
        initial_date = None
        last_checked_row = self._get_last_checked()
        if last_checked_row:
            current_date = datetime.datetime.strptime(last_checked_row.date, "%Y-%m-%d")
            initial_date = current_date - datetime.timedelta(days=14)

        if initial_date and (limit_date.year > initial_date.year):
            initial_date = None

        payload = NotionPayloads.get_data_between_dates(initial_date, limit_date)
        incomplete_rows = self._parse_stats_rows(self.notion_api.query_table(NT_STATS_DB_ID, payload))

        return [row.date for row in incomplete_rows]

    def update_stat(self, stat_data: PersonalStats):
        """Updates a row in the stats database in Notion."""
        date_row = self.notion_api.query_table(NT_STATS_DB_ID, NotionPayloads.get_date_rows(stat_data.date))
        row_id = date_row[0]["id"]

        notion_row_data_raw = self.notion_api.get_table_entry(row_id)
        notion_row_data = self._parse_stats_rows(notion_row_data_raw)[0]

        if stat_data != notion_row_data:
            self.notion_api.update_table_entry(row_id, NotionPayloads.update_stat(stat_data))

    def get_stats_between_dates(self, start_date: datetime.date, end_date: datetime.date) -> List[PersonalStats]:
        raw_data = self.notion_api.query_table(NT_STATS_DB_ID, NotionPayloads.get_data_between_dates(start_date,
                                                                                                     end_date))
        return self._parse_stats_rows(raw_data)
