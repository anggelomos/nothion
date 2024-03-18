from datetime import datetime, timedelta
from typing import List, Optional

from tickthon import Task, ExpenseLog

from nothion import PersonalStats
from nothion._config import NT_TASKS_DB_ID, NT_STATS_DB_ID, NT_NOTES_DB_ID
from nothion._notion_payloads import NotionPayloads
from nothion._notion_table_headers import TasksHeaders, StatsHeaders
from nothion._notion_api import NotionAPI


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

            created_date = ""
            if task_properties[TasksHeaders.CREATED_DATE.value]["date"]:
                created_date = task_properties[TasksHeaders.CREATED_DATE.value]["date"]["start"]

            project_id = ""
            if task_properties[TasksHeaders.PROJECT_ID.value]["rich_text"]:
                project_id = task_properties[TasksHeaders.PROJECT_ID.value]["rich_text"][0]["plain_text"]

            parsed_tasks.append(Task(title=task_properties[TasksHeaders.NOTE.value]["title"][0]["plain_text"],
                                     status=2 if task_properties[TasksHeaders.DONE.value]["checkbox"] else 0,
                                     ticktick_id=task_properties[TasksHeaders.TICKTICK_ID.value]
                                     ["rich_text"][0]["plain_text"],
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

    def get_active_tasks(self) -> List[Task]:
        """Gets all active tasks from Notion that are not done."""
        payload = NotionPayloads.get_active_tasks()

        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)
        notion_tasks = self._parse_notion_tasks(raw_tasks)

        self.active_tasks = notion_tasks
        return notion_tasks

    def get_notion_task(self, ticktick_task: Task) -> Optional[Task]:
        """Gets the task from Notion that have the given ticktick etag."""
        payload = NotionPayloads.get_notion_task(ticktick_task)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)

        notion_tasks = self._parse_notion_tasks(raw_tasks)
        if notion_tasks:
            return notion_tasks[0]
        return None

    def get_notion_task_note(self, ticktick_task: Task) -> Optional[Task]:
        """Gets the task from Notion's notes database that have the given ticktick etag."""
        payload = NotionPayloads.get_notion_task(ticktick_task)
        raw_tasks = self.notion_api.query_table(NT_NOTES_DB_ID, payload)

        notion_tasks = self._parse_notion_tasks(raw_tasks)
        if notion_tasks:
            return notion_tasks[0]
        return None

    def delete_task(self, task: Task):
        """Deletes a task from Notion."""
        task_payload = NotionPayloads.get_notion_task(task)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, task_payload)

        delete_payload = NotionPayloads.delete_table_entry()
        for raw_task in raw_tasks:
            page_id = raw_task["id"]
            self.notion_api.update_table_entry(page_id, delete_payload)

    def delete_task_note(self, task: Task):
        """Deletes a task from Notion."""
        task_payload = NotionPayloads.get_notion_task(task)
        raw_tasks = self.notion_api.query_table(NT_NOTES_DB_ID, task_payload)

        delete_payload = NotionPayloads.delete_table_entry()
        for raw_task in raw_tasks:
            page_id = raw_task["id"]
            self.notion_api.update_table_entry(page_id, delete_payload)

    def get_task_notion_id(self, ticktick_task: Task) -> str:
        """Gets the Notion ID of a task."""
        payload = NotionPayloads.get_notion_task(ticktick_task)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)

        return raw_tasks[0]["id"].replace("-", "")

    def is_task_already_created(self, task: Task) -> bool:
        """Checks if a task is already created in Notion."""
        payload = NotionPayloads.get_notion_task(task)
        raw_tasks = self.notion_api.query_table(NT_TASKS_DB_ID, payload)
        return len(raw_tasks) > 0

    def get_task_note_notion_id(self, ticktick_task: Task) -> str:
        """Gets the Notion ID of a task."""
        payload = NotionPayloads.get_notion_task(ticktick_task)
        raw_tasks = self.notion_api.query_table(NT_NOTES_DB_ID, payload)

        return raw_tasks[0]["id"].replace("-", "")

    def is_task_note_already_created(self, task: Task) -> bool:
        """Checks if a task is already created in Notion."""
        payload = NotionPayloads.get_notion_task(task)
        raw_tasks = self.notion_api.query_table(NT_NOTES_DB_ID, payload)
        return len(raw_tasks) > 0

    def is_highlight_log_already_created(self, task: Task) -> bool:
        """Checks if a highlight log is already created in Notion."""
        payload = NotionPayloads.get_highlight_log(task)
        raw_tasks = self.notion_api.query_table(NT_NOTES_DB_ID, payload)
        return len(raw_tasks) > 0

    def create_task(self, task: Task) -> Optional[dict]:
        """Creates a task in Notion.

        Args:
            task: The task to create.

        Returns:
            The response from Notion if the task was created.
        """

        payload = NotionPayloads.create_task(task)

        if not self.is_task_already_created(task):
            return self.notion_api.create_table_entry(payload)
        return None

    def update_task(self, task: Task):
        """Updates a task in Notion."""
        page_id = self.get_task_notion_id(task)
        payload = NotionPayloads.update_task(task)
        self.notion_api.update_table_entry(page_id, payload)

    def complete_task(self, task: Task):
        page_id = self.get_task_notion_id(task)
        payload = NotionPayloads.complete_task()
        self.notion_api.update_table_entry(page_id, payload)

    def create_task_note(self, task: Task) -> Optional[dict]:
        """Creates a task in the notes database in Notion.

        Args:
            task: The task to create.

        Returns:
            The response from Notion if the task was created.
        """

        payload = NotionPayloads.create_task_note(task)

        if not self.is_task_note_already_created(task):
            return self.notion_api.create_table_entry(payload)
        return None

    def update_task_note(self, task: Task):
        """Updates a task in Notion."""
        page_id = self.get_task_note_notion_id(task)

        notion_task = self.get_notion_task(task)
        is_task_unprocessed = False
        if notion_task:
            is_task_unprocessed = "unprocessed" in notion_task.tags
        payload = NotionPayloads.update_task_note(task, is_task_unprocessed)

        self.notion_api.update_table_entry(page_id, payload)

    def is_note_page_already_created(self, title: str, page_type: str) -> bool:
        """Checks if a note's page is already created in Notion."""
        payload = NotionPayloads.get_note_page(title, page_type)
        raw_tasks = self.notion_api.query_table(NT_NOTES_DB_ID, payload)
        return len(raw_tasks) > 0

    def create_note_page(self, title: str, page_type: str, page_subtype: tuple[str], date: datetime,
                         content: str) -> dict | None:
        """Creates a note page in Notion."""

        payload = NotionPayloads.create_note_page(title, page_type, page_subtype, date, content)

        if not self.is_note_page_already_created(title, page_type):
            return self.notion_api.create_table_entry(payload)
        return None

    def complete_task_note(self, task: Task):
        """Completes a task in Notion."""
        page_id = self.get_task_note_notion_id(task)
        payload = NotionPayloads.complete_task()
        self.notion_api.update_table_entry(page_id, payload)

    def add_expense_log(self, expense_log: ExpenseLog) -> dict:
        """Adds an expense log to the expenses DB in Notion."""
        payload = NotionPayloads.create_expense_log(expense_log)
        return self.notion_api.create_table_entry(payload)

    def add_highlight_log(self, log: Task) -> dict | None:
        """Adds a highlight log to the Notes DB in Notion."""
        payload = NotionPayloads.create_highlight_log(log)

        if not self.is_highlight_log_already_created(log):
            return self.notion_api.create_table_entry(payload)
        return None

    @staticmethod
    def _parse_stats_rows(rows: List[dict] | dict) -> List[PersonalStats]:
        """Parses the raw stats rows from Notion into PersonalStats objects."""
        if not isinstance(rows, List):
            rows = [rows]

        rows_parsed = []
        for row in rows:
            row_properties = row["properties"]
            rows_parsed.append(PersonalStats(date=row_properties[StatsHeaders.DATE.value]["date"]["start"],
                                             weight=row_properties[StatsHeaders.WEIGHT.value]["number"] or 0,
                                             sleep_time=row_properties[StatsHeaders.SLEEP_TIME.value]["number"] or 0,
                                             work_time=row_properties[StatsHeaders.WORK_TIME.value]["number"] or 0,
                                             leisure_time=row_properties[StatsHeaders.LEISURE_TIME.value]
                                                                        ["number"] or 0,
                                             focus_time=row_properties[StatsHeaders.FOCUS_TIME.value]["number"] or 0))
        return rows_parsed

    def _get_last_stats_row_checked(self) -> Optional[PersonalStats]:
        """Gets the last checked row from the stats in Notion database."""
        checked_rows = self.notion_api.query_table(NT_STATS_DB_ID, NotionPayloads.get_checked_stats_rows())
        if checked_rows:
            return self._parse_stats_rows(checked_rows[-1])[0]
        return None

    def get_incomplete_stats_dates(self, limit_date: datetime) -> List[str]:
        """Gets the dates that are incomplete in the stats database starting 14 days before the limit date.

        Args:
            limit_date: The limit date that is checked to get the incomplete dates.

        Returns:
            A list of dates in format YYYY-MM-DD.
        """
        initial_date = datetime(limit_date.year, 1, 1)
        last_checked_row = self._get_last_stats_row_checked()
        if last_checked_row:
            current_date = datetime.strptime(last_checked_row.date, "%Y-%m-%d")
            initial_date = current_date - timedelta(days=14)

        dates = []
        delta = limit_date - initial_date
        for delta_days in range(delta.days + 1):
            day = initial_date + timedelta(days=delta_days)
            dates.append(day.strftime("%Y-%m-%d"))

        return dates

    def update_stats(self, stat_data: PersonalStats):
        """Updates a row in the stats database in Notion."""
        date_row = self.notion_api.query_table(NT_STATS_DB_ID, NotionPayloads.get_date_rows(stat_data.date))

        if date_row:
            row_id = date_row[0]["id"]
            self.notion_api.update_table_entry(row_id, NotionPayloads.update_stats_row(stat_data, new_row=False))
        else:
            self.notion_api.create_table_entry(NotionPayloads.update_stats_row(stat_data, new_row=True))

    def get_stats_between_dates(self, start_date: datetime, end_date: datetime) -> List[PersonalStats]:
        raw_data = self.notion_api.query_table(NT_STATS_DB_ID, NotionPayloads.get_data_between_dates(start_date,
                                                                                                     end_date))
        return self._parse_stats_rows(raw_data)

    @staticmethod
    def _parse_notion_block(block: dict) -> str:
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

    def _get_all_block_children(self, block_id: str) -> list:
        """Recursively gets the children of a block in Notion.

        Args:
            block_id: The ID of the block to get the children from.

        Returns:
            A list of children of the block.
        """
        children = []
        children_data = self.notion_api.get_block_children(block_id)

        for child in children_data.get("results", []):
            parsed_child: list[str | list] = [self._parse_notion_block(child)]
            children.append(parsed_child)

            if child.get("has_children", False):
                parsed_child.append(self._get_all_block_children(child["id"]))

        return children

    def get_daily_journal_data(self, date: datetime) -> dict:
        """"Gets the page data of a daily journal entry for a specific date."""
        journal_entry = self.notion_api.query_table(NT_NOTES_DB_ID, NotionPayloads.get_daily_journal_entry(date))
        return journal_entry[0]

    def get_daily_journal_content(self, date: datetime) -> list:
        """Gets the content of a journal entry for a specific date."""
        journal_entry = self.get_daily_journal_data(date)["id"]
        return self._get_all_block_children(journal_entry)
