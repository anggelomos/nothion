# Nothion
Yet another unofficial Notion API client

## Installation
```bash
pip install nothion
```

## Usage
```python
from nothion import NotionClient

client = NotionClient(auth_secret)
client.get_active_tasks()
```

## Features
- get_active_tasks()
- get_task_by_id(task_id)
- get_notion_id(task_id)
- is_task_already_created(task_id)
- create_task(Task)
- update_task(task_id, Task)
- delete_task(task_id)
- add_expense_log(title, amount, date)
- get_incomplete_stats_dates(date)
- update_stats_row(date: str, stats_data: StatsData)
- get_data_between_dates(start_date: str, end_date: str)


## Personal Stats model
This packages uses a custom attrs model to store personal stats, it has the following attributes:

PersonalStats:
- time_stats: TimeStats
- weight: float

TimeStats:
- work_time: float
- leisure_time: float
- focus_time: float
