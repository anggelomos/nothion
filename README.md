# Nothion
Yet another unofficial Notion API client.

## Installation
```bash
pip install nothion
```

## Usage
```python
from nothion import NotionClient

client = NotionClient(auth_secret="your_auth_token",
                      tasks_db_id: str | None = None,
                      stats_db_id: str | None = None,
                      notes_db_id: str | None = None,
                      expenses_db_id: str | None = None)
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
- get_incomplete_dates(limit_date: datetime) -> List[str]
- update(stat_data: PersonalStats, overwrite_stats: bool = False)
- get_between_dates(start_date: datetime, end_date: datetime) -> List[PersonalStats]

### Expenses Handler
- add_expense_log(expense_log: ExpenseLog)

## Data Models

### PersonalStats
This package uses a custom attrs model to store personal stats:

- date: str
- time_stats: TimeStats
- weight: float

#### TimeStats
- work_time: float
- leisure_time: float
- focus_time: float

### ExpenseLog
This package uses a custom attrs model to store expense log data:

- fecha: str
- egresos: float
- producto: str

## Environment Variables

- NT_AUTH: Notion auth token, for example secret_t1CdN9S8yicG5eWLUOfhcWaOscVnFXns.
