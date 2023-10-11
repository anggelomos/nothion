from enum import Enum


class ExpensesHeaders(Enum):
    PRODUCT = "product"
    EXPENSE = "expense"
    DATE = "date"


class TasksHeaders(Enum):
    DONE = "Done"
    TASK = "Task"
    FOCUS_TIME = "Focus time"
    DUE_DATE = "Due date"
    TAGS = "Tags"
    TICKTICK_ID = "Ticktick id"
    TICKTICK_ETAG = "Ticktick etag"
    PROJECT_ID = "Project id"
    TIMEZONE = "Timezone"


class StatsHeaders(Enum):
    COMPLETED = "completed"
    DATE = "date"
    WORK_TIME = "work time"
    FOCUS_TIME = "focus time"
    LEISURE_TIME = "leisure time"
    WEIGHT = "weight"
