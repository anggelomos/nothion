import json
from datetime import datetime
from typing import Optional

from tickthon import Task, ExpenseLog

from nothion._notion_table_headers import TasksHeaders, ExpensesHeaders, StatsHeaders, NotesHeaders
from nothion.personal_stats_model import PersonalStats


class NotionPayloads:
    def __init__(self, tasks_db_id: str, expenses_db_id: str, stats_db_id: str, notes_db_id: str):
        self.tasks_db_id = tasks_db_id
        self.expenses_db_id = expenses_db_id
        self.stats_db_id = stats_db_id
        self.notes_db_id = notes_db_id

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
                TasksHeaders.COLUMN_ID.value: {"rich_text": [{"text": {"content": task.column_id}}]},
                TasksHeaders.PROJECT_ID.value: {"rich_text": [{"text": {"content": task.project_id}}]},
                TasksHeaders.TICKTICK_ETAG.value: {"rich_text": [{"text": {"content": task.ticktick_etag}}]},
                TasksHeaders.CREATED_DATE.value: {"date": {"start": task.created_date}},
                TasksHeaders.TIMEZONE.value: {"rich_text": [{"text": {"content": task.timezone}}]},
            }
        }

        if task.due_date:
            payload["properties"][TasksHeaders.DUE_DATE.value] = {"date": {"start": task.due_date}}

        return payload

    def create_task(self, task: Task) -> str:
        payload = self._base_task_payload(task)
        payload["parent"] = {"database_id": self.tasks_db_id}
        return json.dumps(payload)

    def create_task_note(self, task: Task) -> str:
        payload = self._base_task_payload(task)
        payload["parent"] = {"database_id": self.notes_db_id}
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
    def get_highlight_log(log: Task) -> dict:
        """Payload to get a highlight note.

        Args:
            log: The task to search for.
        """
        date_without_seconds = datetime.fromisoformat(log.created_date).replace(second=0, microsecond=0).isoformat()
        payload = {"filter": {
            "and": [{"property": NotesHeaders.NOTE.value,
                     "rich_text": {"equals": log.title}},
                    {"property": NotesHeaders.TYPE.value,
                     "select": {"equals": "highlight"}
                     },
                    {"property": NotesHeaders.DUE_DATE.value,
                     "date": {"equals": date_without_seconds}
                     },
                    ]}}

        return payload

    def create_highlight_log(self, log: Task) -> str:
        payload = {
            "parent": {"database_id": self.notes_db_id},
            "icon": {"type": "emoji", "emoji": "✨"},
            "properties": {
                NotesHeaders.NOTE.value: {"title": [{"text": {"content": log.title}}]},
                NotesHeaders.TYPE.value: {"select": {"name": "highlight"}},
                NotesHeaders.DUE_DATE.value: {"date": {"start": log.created_date}}
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

        if new_row or overwrite_stats:
            payload["properties"].update({
                StatsHeaders.FOCUS_TOTAL_TIME.value: {"number": stat.focus_total_time},
                StatsHeaders.FOCUS_ACTIVE_TIME.value: {"number": stat.focus_active_time},
                StatsHeaders.WORK_TIME.value: {"number": stat.work_time},
                StatsHeaders.LEISURE_TIME.value: {"number": stat.leisure_time},
                StatsHeaders.SLEEP_TIME_AMOUNT.value: {"number": stat.sleep_time_amount},
                StatsHeaders.FALL_ASLEEP_TIME.value: {"number": stat.fall_asleep_time},
                StatsHeaders.SLEEP_SCORE.value: {"number": stat.sleep_score},
                StatsHeaders.WEIGHT.value: {"number": stat.weight},
                StatsHeaders.STEPS.value: {"number": stat.steps},
                StatsHeaders.WATER_CUPS.value: {"number": stat.water_cups},
            })
        elif old_stats:
            stats_fields = [header for header in StatsHeaders if header != StatsHeaders.DATE]

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
