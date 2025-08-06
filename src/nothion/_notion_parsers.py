from tickthon import Task

from nothion._notion_table_headers import StatsHeaders, TasksHeaders
from nothion.data_models.personal_stats import PersonalStats


class NotionParsers:

    @staticmethod
    def _get_rich_text(properties: dict, field: str) -> str:
        """Extracts plain text from rich text field."""
        try:
            rich_text = properties[field]["rich_text"]
            return rich_text[0]["plain_text"] if rich_text else ""
        except (KeyError, IndexError):
            return ""

    @staticmethod
    def _get_date(properties: dict, field: str) -> str:
        """Extracts start date from date field."""
        try:
            date_field = properties[field]

            if date_field.get("date"):
                parsed_date = date_field["date"]["start"]
            elif date_field.get("created_time"):
                parsed_date = date_field["created_time"].split("T")[0]
            elif date_field.get("last_edited_time"):
                parsed_date = date_field["last_edited_time"].split("T")[0]
            else:
                parsed_date = ""

            return parsed_date
        except KeyError:
            return ""

    @staticmethod
    def _get_title(properties: dict, field: str) -> str:
        """Extracts plain text from title field."""
        try:
            title = properties[field]["title"]
            return title[0]["plain_text"] if title else ""
        except (KeyError, IndexError):
            return ""

    @staticmethod
    def _get_number(properties: dict, field: str) -> float:
        """Extracts number from number field."""
        try:
            return properties[field]["number"] or 0
        except KeyError:
            return 0

    @classmethod
    def parse_notion_tasks(cls, raw_tasks: list[dict]) -> list[Task]:
        """Parses the raw tasks from Notion into Task objects.

        Args:
            raw_tasks: A single task dict or list of task dicts from Notion API

        Returns:
            List[Task]: List of parsed Task objects
        """

        parsed_tasks = []
        for raw_task in raw_tasks:
            try:
                task_properties = raw_task["properties"]

                parsed_tasks.append(Task(
                    title=cls._get_title(task_properties, TasksHeaders.TITLE.value),
                    status=2 if task_properties.get(TasksHeaders.DONE.value, {}).get("checkbox", False) else 0,
                    ticktick_id="",
                    ticktick_etag="",
                    column_id=cls._get_rich_text(task_properties, TasksHeaders.COLUMN_ID.value),
                    created_date=cls._get_date(task_properties, TasksHeaders.CREATED_DATE.value),
                    focus_time=cls._get_number(task_properties, TasksHeaders.FOCUS_TIME.value),
                    deleted=int(raw_task.get("archived", False)),
                    tags=tuple(tag["name"] for tag in
                               task_properties.get(TasksHeaders.TAGS.value, {}).get("multi_select", [])),
                    project_id=cls._get_rich_text(task_properties, TasksHeaders.PROJECT_ID.value),
                    due_date=cls._get_date(task_properties, TasksHeaders.DATE.value)
                ))
            except Exception as e:
                print(f"Error parsing task: {e}")
                continue

        return parsed_tasks

    @classmethod
    def parse_stats_rows(cls, rows: list[dict]) -> list[PersonalStats]:
        """Parses the raw stats rows from Notion into PersonalStats objects."""

        rows_parsed = []
        for row in rows:
            try:
                row_properties = row["properties"]

                rows_parsed.append(
                    PersonalStats(
                        date=cls._get_date(row_properties, StatsHeaders.DATE.value),
                        focus_total_time=cls._get_number(row_properties, StatsHeaders.FOCUS_TOTAL_TIME.value),
                        focus_personal_time=cls._get_number(row_properties, StatsHeaders.FOCUS_PERSONAL_TIME.value),
                        focus_work_time=cls._get_number(row_properties, StatsHeaders.FOCUS_WORK_TIME.value),
                        work_time=cls._get_number(row_properties, StatsHeaders.WORK_TIME.value),
                        leisure_time=cls._get_number(row_properties, StatsHeaders.LEISURE_TIME.value),
                        sleep_time_amount=cls._get_number(row_properties, StatsHeaders.SLEEP_TIME_AMOUNT.value),
                        sleep_deep_amount=cls._get_number(row_properties, StatsHeaders.SLEEP_DEEP_AMOUNT.value),
                        fall_asleep_time=cls._get_number(row_properties, StatsHeaders.FALL_ASLEEP_TIME.value),
                        sleep_score=cls._get_number(row_properties, StatsHeaders.SLEEP_SCORE.value),
                        weight=cls._get_number(row_properties, StatsHeaders.WEIGHT.value),
                        steps=cls._get_number(row_properties, StatsHeaders.STEPS.value),
                        water_cups=int(cls._get_number(row_properties, StatsHeaders.WATER_CUPS.value)),
                    )
                )
            except Exception as e:
                print(f"Error parsing stats row: {e}")
                continue

        return rows_parsed

    @classmethod
    def parse_block(cls, block: dict) -> str:
        """Parses a block from Notion into a string."""
        try:
            block_type = block["type"]
            block_text = cls._get_rich_text(block[block_type], "rich_text")

            if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
                return block_text
            elif block_type == "bulleted_list_item":
                return "- " + block_text
            elif block_type == "toggle":
                return "> " + block_text
            return block_type
        except Exception as e:
            print(f"Error parsing block: {e}")
            return ""
