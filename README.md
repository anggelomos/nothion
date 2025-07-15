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
- get_task(ticktick_task: Task)
- get_notion_id(ticktick_task: Task)
- is_task_already_created(task: Task)
- create(task: Task)
- update_task(task: Task)
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

### Blocks Handler
- get_all_children(block_id: str) -> list

## Data Models

### PersonalStats
This package uses a custom attrs model to store personal stats:

- date: str
- focus_total_time: float | None
- focus_active_time: float | None  
- work_time: float | None
- leisure_time: float | None
- sleep_time_amount: float | None
- sleep_deep_amount: float | None
- fall_asleep_time: float | None
- sleep_score: float | None
- weight: float | None
- steps: float | None
- water_cups: int | None

### ExpenseLog
This package uses a custom attrs model to store expense log data:

- date: str
- expense: float
- product: str

## Environment Variables

- NT_AUTH: Notion auth token, for example secret_t1Cd...
