# Nothion
Yet another unofficial Notion API client.

## Installation
```bash
pip install nothion
```

## Usage
```python
from nothion import NotionClient

client = NotionClient(auth_secret="your_auth_token")
client.tasks.get_active_tasks()
```

## Features

### Tasks Handler
- get_active_tasks()
- get_notion_task(ticktick_task: Task)
- get_notion_id(ticktick_task: Task)
- is_already_created(task: Task)
- create(task: Task)
- update(task: Task)
- complete(task: Task)
- delete(task: Task)

### Notes Handler
- is_page_already_created(title: str, page_type: str)
- create_page(title: str, page_type: str, page_subtype: tuple[str], date: datetime, content: str)

### Stats Handler
- get_incomplete_dates(limit_date: datetime)
- update(stat_data: PersonalStats, overwrite_stats: bool = False)
- get_between_dates(start_date: datetime, end_date: datetime)

### Expenses Handler
- add_expense_log(expense_log: ExpenseLog)

## Personal Stats model
This package uses a custom attrs model to store personal stats, it has the following attributes:

PersonalStats:
- time_stats: TimeStats
- weight: float

TimeStats:
- work_time: float
- leisure_time: float
- focus_time: float

## ExpenseLog model
This package uses a custom attrs model to store expense log data, it has the following attributes:

ExpenseLog:
- fecha: str
- egresos: float
- producto: str

## Environment variables

- NT_AUTH: Notion auth token, for example secret_t1CdN9S8yicG5eWLUOfhcWaOscVnFXns.
- NT_TASKS_DB_ID: Notion tasks database id
- NT_NOTES_DB_ID: Notion notes database id
- NT_STATS_DB_ID: Notion stats database id
- NT_EXPENSES_DB_ID: Notion expenses database id
