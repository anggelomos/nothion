import json
import datetime
from typing import Optional

from tickthon import Task

from ._config import NT_TASKS_DB_ID, NT_EXPENSES_DB_ID, NT_STATS_DB_ID
from ._notion_table_headers import TasksHeaders, ExpensesHeaders, StatsHeaders
from .expense_log_model import ExpenseLog
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
                TasksHeaders.RECURRENT_ID.value: {"rich_text": [{"text": {"content": task.recurrent_id}}]},
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
    def update_task(cls, task: Task) -> str:
        return json.dumps(cls._base_task_payload(task))

    @staticmethod
    def delete_table_entry() -> str:
        payload = {"archived": True}

        return json.dumps(payload)

    @staticmethod
    def get_task_by_id(task_id: str, due_date: str = "") -> dict:
        """Payload to get a task by its ticktick id.

        Args:
            task_id: The ticktick id of the task. For example: 6f8a2b3c4d5e1f09a7b6c8d9e0f2
            due_date: The due date of the task in format YYYY-MM-DD.
        """
        filters = [{"property": TasksHeaders.TICKTICK_ID.value, "rich_text": {"equals": task_id}}]

        if due_date:
            filters.append({"property": TasksHeaders.DUE_DATE.value, "date": {"equals": due_date}})

        payload = {"sorts": [{"property": TasksHeaders.DUE_DATE.value, "direction": "ascending"}],
                   "filter": {"and": filters}}

        return payload

    @staticmethod
    def create_stat_row(personal_stats: PersonalStats) -> str:
        payload = {
            "parent": {"database_id": NT_STATS_DB_ID},
            "properties": {
                StatsHeaders.DATE.value: {"date": {"start": personal_stats.date}},
                StatsHeaders.WORK_TIME.value: {"number": personal_stats.time_stats.work_time},
                StatsHeaders.LEISURE_TIME.value: {"number": personal_stats.time_stats.leisure_time},
                StatsHeaders.FOCUS_TIME.value: {"number": personal_stats.time_stats.focus_time},
            }
        }

        return json.dumps(payload)

    @staticmethod
    def create_expense_log(expense_log: ExpenseLog) -> str:
        payload = {
            "parent": {"database_id": NT_EXPENSES_DB_ID},
            "properties": {
                ExpensesHeaders.PRODUCTO.value: {"title": [{"text": {"content": expense_log.producto}}]},
                ExpensesHeaders.EGRESOS.value: {"number": expense_log.egresos},
                ExpensesHeaders.FECHA.value: {"date": {"start": expense_log.fecha}}
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
                StatsHeaders.WORK_TIME.value: {"number": stat.time_stats.work_time},
                StatsHeaders.LEISURE_TIME.value: {"number": stat.time_stats.leisure_time},
                StatsHeaders.FOCUS_TIME.value: {"number": stat.time_stats.focus_time},
            }
        }

        return json.dumps(payload)
