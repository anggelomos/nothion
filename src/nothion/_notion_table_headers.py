from enum import Enum


class ExpensesHeaders(Enum):
    PRODUCT = "item"
    EXPENSE = "expense"
    DATE = "date"


class TasksHeaders(Enum):
    DONE = "Done"
    NOTE = "Note"
    FOCUS_TIME = "Focus time"
    DUE_DATE = "Due date"
    CREATED_DATE = "Created date"
    TAGS = "Tags"
    TICKTICK_ID = "Ticktick id"
    COLUMN_ID = "Column id"
    TICKTICK_ETAG = "Ticktick etag"
    PROJECT_ID = "Project id"
    TIMEZONE = "Timezone"


class StatsHeaders(Enum):
    COMPLETED = "completed"
    DATE = "date"
    WORK_TIME = "work time"
    SLEEP_TIME = "sleep time"
    FOCUS_TIME = "focus time"
    LEISURE_TIME = "leisure time"
    WEIGHT = "weight"


class NotesHeaders(Enum):
    NOTE = "Note"
    TYPE = "Type"
    SUBTYPE = "Sub-type"
    DUE_DATE = "Due date"
