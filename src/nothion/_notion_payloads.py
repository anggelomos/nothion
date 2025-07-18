import json
from datetime import datetime
from typing import Optional

from tickthon import Task

from nothion._notion_table_headers import TasksHeaders, ExpensesHeaders, StatsHeaders, NotesHeaders
from nothion.data_models.expense_log import ExpenseLog
from nothion.data_models.personal_stats import PersonalStats


class NotionPayloads:
    def __init__(self, tasks_db_id: str, expenses_db_id: str, stats_db_id: str, notes_db_id: str):
        self.tasks_db_id = tasks_db_id
        self.expenses_db_id = expenses_db_id
        self.stats_db_id = stats_db_id
        self.notes_db_id = notes_db_id

    @staticmethod
    def get_active_tasks() -> dict:
        tag_values = ["work-project", "dwtask", "swtask", "personal-project", "dtask", "stask", "wørk-focus-meeting"]

        return {
            "filter": {
                "or": [
                    {
                        "property": "Tag",
                        "multi_select": {
                            "contains": tag
                        }
                    } for tag in tag_values
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
                TasksHeaders.COLUMN_ID.value: {"rich_text": [{"text": {"content": task.column_id}}]},
                TasksHeaders.PROJECT_ID.value: {"rich_text": [{"text": {"content": task.project_id}}]},
                TasksHeaders.CREATED_DATE.value: {"date": {"start": task.created_date}},
            }
        }

        if task.due_date:
            payload["properties"][TasksHeaders.DATE.value] = {"date": {"start": task.due_date}}

        return payload

    def create_task(self, task: Task) -> str:
        payload = self._base_task_payload(task)
        payload["parent"] = {"database_id": self.tasks_db_id}
        return json.dumps(payload)

    @classmethod
    def update_task(cls, task: Task) -> str:
        payload = {
            "properties": {
                TasksHeaders.FOCUS_TIME.value: {"number": task.focus_time},
                TasksHeaders.COLUMN_ID.value: {"rich_text": [{"text": {"content": task.column_id}}]},
                TasksHeaders.PROJECT_ID.value: {"rich_text": [{"text": {"content": task.project_id}}]},
            }
        }

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
        payload = {
            "sorts": [{"property": TasksHeaders.DATE.value, "direction": "ascending"}],
            "filter": {
                "and": [
                    {"property": TasksHeaders.TITLE.value, "rich_text": {"equals": task.title}}
                ]
            }
        }

        return payload

    def create_expense_log(self, expense_log: ExpenseLog) -> str:
        payload = {
            "parent": {"database_id": self.expenses_db_id},
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
            "sorts": [{"property": StatsHeaders.DATE.value, "direction": "descending"}],
            "filter": {"and": [{"property": StatsHeaders.COMPLETED.value, "checkbox": {"equals": True}}]},
            "page_size": 1
        }
        return payload

    @staticmethod
    def get_data_between_dates(initial_date: Optional[datetime], today_date: datetime) -> dict:
        filters = []
        if initial_date:
            filters.append({"property": "date", "date": {"on_or_after": initial_date.strftime("%Y-%m-%d")}})

        filters.append({"property": "date", "date": {"on_or_before": today_date.strftime("%Y-%m-%d")}})

        return {"sorts": [{"property": "day #", "direction": "ascending"}], "filter": {"and": filters}}

    @staticmethod
    def get_date_rows(date: str) -> dict:
        return {"filter": {"and": [{"property": "date", "date": {"equals": date}}]}}

    def update_stats_row(self,
                         stat: PersonalStats,
                         old_stats: PersonalStats | None = None,
                         new_row: bool = False,
                         overwrite_stats: bool = False) -> str:
        payload: dict = {
            "properties": {
                StatsHeaders.DATE.value: {"date": {"start": stat.date}}
            }
        }

        stats_fields = [header for header in StatsHeaders if header != StatsHeaders.DATE]
        if new_row or overwrite_stats:

            for header in stats_fields:
                attr_name = header.name.lower()
                new_value = getattr(stat, attr_name, None)

                if new_value is not None:
                    payload["properties"][header.value] = {"number": new_value}

        elif old_stats:

            for header in stats_fields:
                attr_name = header.name.lower()

                old_value = getattr(old_stats, attr_name, None)
                new_value = getattr(stat, attr_name, None)

                if old_value and not new_value:
                    payload["properties"][header.value] = {"number": old_value}

        if new_row:
            payload["parent"] = {"database_id": self.stats_db_id}

        return json.dumps(payload)

    def create_note_page(self, title: str, page_type: str, page_subtype: tuple[str], date: datetime,
                         content: str) -> str:
        content_block = {"object": "block",
                         "type": "paragraph",
                         "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                         }

        payload = {
            "parent": {"database_id": self.notes_db_id},
            "properties": {
                NotesHeaders.NOTE.value: {"title": [{"text": {"content": title}}]},
                NotesHeaders.TYPE.value: {"select": {"name": page_type}},
                NotesHeaders.SUBTYPE.value: {"multi_select": [{"name": st} for st in page_subtype]},
                NotesHeaders.DUE_DATE.value: {"date": {"start": date.strftime("%Y-%m-%d")}},
            },
            "children": [content_block]
        }

        return json.dumps(payload)

    @classmethod
    def get_note_page(cls, title: str, page_type: str) -> dict:
        return {"filter": {
                    "and": [{"property": NotesHeaders.NOTE.value,
                             "rich_text": {"equals": title}},
                            {"property": NotesHeaders.TYPE.value,
                             "select": {"equals": page_type}
                             },
                            ]
                        }
                }
