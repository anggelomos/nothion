from enum import Enum


class ExpensesHeaders(Enum):
    PRODUCT = "item"
    EXPENSE = "expense"
    DATE = "date"


class TasksHeaders(Enum):
    DONE = "Checkbox"
    TITLE = "Title"
    FOCUS_TIME = "Focus time"
    DATE = "Date"
    CREATED_DATE = "Created time"
    TAGS = "Tag"
    PROJECT_ID = "List id"
    COLUMN_ID = "Column id"


class StatsHeaders(Enum):
    COMPLETED = "completed"
    DATE = "date"
    FOCUS_TOTAL_TIME = "ftt - focus time total"
    FOCUS_PERSONAL_TIME = "ftp - focus time personal"
    FOCUS_WORK_TIME = "ftw - focus time work"
    WORK_TIME = "ftr - focus time rescuetime"
    LEISURE_TIME = "lt - leisure time"
    SLEEP_TIME_AMOUNT = "sa - sleep amount"
    SLEEP_DEEP_AMOUNT = "sda - sleep deep amount"
    SLEEP_REM_AMOUNT = "sra - sleep rem amount"
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
