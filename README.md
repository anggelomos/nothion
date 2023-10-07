# Nothion
Yet another unofficial Notion API client

## Installation
```bash
pip install nothion
```

## Usage
```python
from nothion import NotionClient

client = NotionClient()
client.get_active_tasks()
```

## Features
- get_active_tasks()
- get_tasks_by_id(task_id)
- get_task_notion_id(task_id)
- is_task_already_created(ticktick_id, due_date)
- create_task(Task)
- update_task(Task)
- delete_task(task_id)
- add_expense_log(ExpenseLog)
- get_incomplete_stats_dates(date)
- update_stat(PersonalStats)
- get_stats_between_dates(start_date, end_date)


## Personal Stats model
This packages uses a custom attrs model to store personal stats, it has the following attributes:

PersonalStats:
- time_stats: TimeStats
- weight: float

TimeStats:
- work_time: float
- leisure_time: float
- focus_time: float

## ExpenseLog model
This packages uses a custom attrs model to store expense log data, it has the following attributes:

ExpenseLog:
- fecha: str
- egresos: float
- producto: str

## Environment variables

- NT_AUTH: Notion auth token, for example secret_t1CdN9S8yicG5eWLUOfhcWaOscVnFXns.
- NT_TASKS_DB_ID: Notion tasks database id
- NT_STATS_DB_ID: Notion stats database id
- NT_EXPENSES_DB_ID: Notion expenses database id
