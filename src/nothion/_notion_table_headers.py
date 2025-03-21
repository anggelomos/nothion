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
    FOCUS_TOTAL_TIME = "ftt - focus time total"
    FOCUS_ACTIVE_TIME = "fta - focus time active"
    WORK_TIME = "ftr - focus time rescuetime"
    LEISURE_TIME = "lt - leisure time"
    SLEEP_TIME_AMOUNT = "sa - sleep amount"
    FALL_ASLEEP_TIME = "st - fall asleep time"
    SLEEP_SCORE = "ss - sleep score"
    WEIGHT = "kg - weight"
    STEPS = "stp - steps"
    WATER_CUPS = "wc - water cups"


class NotesHeaders(Enum):
    NOTE = "Note"
    TYPE = "Type"
    SUBTYPE = "Sub-type"
    DUE_DATE = "Due date"
