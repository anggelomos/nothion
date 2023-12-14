import json
import datetime
from typing import Optional

from tickthon import Task, ExpenseLog

from ._config import NT_TASKS_DB_ID, NT_EXPENSES_DB_ID, NT_STATS_DB_ID, NT_NOTES_DB_ID
from ._notion_table_headers import TasksHeaders, ExpensesHeaders, StatsHeaders
from .personal_stats_model import PersonalStats


class NotionPayloads:

    @staticmethod
    def get_active_tasks() -> dict:
        return {
            "filter": {
                "and": [
                    {
                        "property": TasksHeaders.DONE.value,
                        "checkbox": {
                            "equals": False
                        }
                    }
                ]
            }
        }

    @staticmethod
    def _base_task_payload(task: Task) -> dict:
        payload = {
            "properties": {
                TasksHeaders.DONE.value: {"checkbox": task.status != 0},
                "title": {"title": [{"text": {"content": task.title}}]},
                TasksHeaders.FOCUS_TIME.value: {"number": task.focus_time},
                TasksHeaders.TAGS.value: {"multi_select": list(map(lambda tag: {"name": tag}, task.tags))},
                TasksHeaders.TICKTICK_ID.value: {"rich_text": [{"text": {"content": task.ticktick_id}}]},
                TasksHeaders.PROJECT_ID.value: {"rich_text": [{"text": {"content": task.project_id}}]},
                TasksHeaders.TICKTICK_ETAG.value: {"rich_text": [{"text": {"content": task.ticktick_etag}}]},
                TasksHeaders.CREATED_DATE.value: {"date": {"start": task.created_date}},
                TasksHeaders.TIMEZONE.value: {"rich_text": [{"text": {"content": task.timezone}}]},
            }
        }

        if task.due_date:
            payload["properties"][TasksHeaders.DUE_DATE.value] = {"date": {"start": task.due_date}}

        return payload

    @classmethod
    def create_task(cls, task: Task) -> str:
        payload = cls._base_task_payload(task)
        payload["parent"] = {"database_id": NT_TASKS_DB_ID}
        return json.dumps(payload)

    @classmethod
    def create_task_note(cls, task: Task) -> str:
        payload = cls._base_task_payload(task)
        payload["parent"] = {"database_id": NT_NOTES_DB_ID}
        payload["properties"][TasksHeaders.TAGS.value]["multi_select"].append({"name": "unprocessed"})
        return json.dumps(payload)

    @classmethod
    def update_task(cls, task: Task) -> str:
        return json.dumps(cls._base_task_payload(task))

    @classmethod
    def update_task_note(cls, task: Task, is_task_unprocessed: bool) -> str:
        payload = cls._base_task_payload(task)
        if is_task_unprocessed:
            payload["properties"][TasksHeaders.TAGS.value]["multi_select"].append({"name": "unprocessed"})

        return json.dumps(payload)

    @classmethod
    def complete_task(cls) -> str:
        payload = {"properties": {TasksHeaders.DONE.value: {"checkbox": True}}}
        return json.dumps(payload)

    @staticmethod
    def delete_table_entry() -> str:
        payload = {"archived": True}

        return json.dumps(payload)

    @staticmethod
    def get_notion_task(task: Task) -> dict:
        """Payload to get a notion task by its ticktick id or etag.

        Args:
            task: The task to search for.
        """
        ticktick_etag = task.ticktick_etag if task.ticktick_etag else "no-etag-found"
        ticktick_id = task.ticktick_id if task.ticktick_id else "no-ticktick-id-found"
        payload = {"sorts": [{"property": TasksHeaders.DUE_DATE.value, "direction": "ascending"}],
                   "filter": {
                       "or": [{"property": TasksHeaders.TICKTICK_ETAG.value,
                               "rich_text": {"equals": ticktick_etag}},
                              {"property": TasksHeaders.TICKTICK_ID.value,
                               "rich_text": {"equals": ticktick_id}}
                              ]}
                   }

        return payload

    @staticmethod
    def create_stat_row(personal_stats: PersonalStats) -> str:
        payload = {
            "parent": {"database_id": NT_STATS_DB_ID},
            "properties": {
                StatsHeaders.DATE.value: {"date": {"start": personal_stats.date}},
                StatsHeaders.WORK_TIME.value: {"number": personal_stats.work_time},
                StatsHeaders.LEISURE_TIME.value: {"number": personal_stats.leisure_time},
                StatsHeaders.FOCUS_TIME.value: {"number": personal_stats.focus_time},
            }
        }

        return json.dumps(payload)

    @staticmethod
    def create_expense_log(expense_log: ExpenseLog) -> str:
        payload = {
            "parent": {"database_id": NT_EXPENSES_DB_ID},
            "properties": {
                ExpensesHeaders.PRODUCT.value: {"title": [{"text": {"content": expense_log.product}}]},
                ExpensesHeaders.EXPENSE.value: {"number": expense_log.expense},
                ExpensesHeaders.DATE.value: {"date": {"start": expense_log.date}}
            }
        }

        return json.dumps(payload)

    @staticmethod
    def get_checked_stats_rows() -> dict:
        payload = {
            "sorts": [{"property": StatsHeaders.DATE.value, "direction": "ascending"}],
            "filter": {"and": [{"property": StatsHeaders.COMPLETED.value, "checkbox": {"equals": True}}]}
        }
        return payload

    @staticmethod
    def get_data_between_dates(initial_date: Optional[datetime.date], today_date: datetime.date) -> dict:
        filters = []
        if initial_date:
            filters.append({"property": "date", "date": {"on_or_after": initial_date.strftime("%Y-%m-%d")}})

        filters.append({"property": "date", "date": {"on_or_before": today_date.strftime("%Y-%m-%d")}})

        return {"sorts": [{"property": "day #", "direction": "ascending"}], "filter": {"and": filters}}

    @staticmethod
    def get_date_rows(date: str) -> dict:
        return {"filter": {"and": [{"property": "date", "date": {"equals": date}}]}}

    @staticmethod
    def update_stat(stat: PersonalStats) -> str:
        payload = {
            "properties": {
                StatsHeaders.DATE.value: {"date": {"start": stat.date}},
                StatsHeaders.WEIGHT.value: {"number": stat.weight},
                StatsHeaders.WORK_TIME.value: {"number": stat.work_time},
                StatsHeaders.LEISURE_TIME.value: {"number": stat.leisure_time},
                StatsHeaders.FOCUS_TIME.value: {"number": stat.focus_time},
            }
        }

        return json.dumps(payload)
