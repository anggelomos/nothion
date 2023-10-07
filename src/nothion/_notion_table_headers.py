from enum import Enum


class ExpensesHeaders(Enum):
    PRODUCTO = "producto"
    EGRESOS = "egresos"
    FECHA = "fecha"


class TasksHeaders(Enum):
    DONE = "Done"
    TASK = "Task"
    FOCUS_TIME = "Focus time"
    DUE_DATE = "Due date"
    TAGS = "Tags"
    TICKTICK_ID = "Ticktick id"
    RECURRENT_ID = "Recurrent id"
    PROJECT_ID = "Project id"
    TIMEZONE = "Timezone"


class StatsHeaders(Enum):
    COMPLETED = "completed"
    DATE = "date"
    WORK_TIME = "work time"
    FOCUS_TIME = "focus time"
    LEISURE_TIME = "leisure time"
    WEIGHT = "weight"
