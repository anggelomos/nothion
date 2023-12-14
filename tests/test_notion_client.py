import random
from datetime import datetime, timedelta, date
from typing import List
from uuid import uuid4

import pytest
from nothion import NotionClient, PersonalStats
from tickthon import Task, ExpenseLog

from nothion._notion_payloads import NotionPayloads
from nothion._notion_table_headers import ExpensesHeaders


@pytest.fixture(scope="module")
def notion_client(notion_info):
    return NotionClient(notion_info["auth_secret"])


def test_get_active_tasks(notion_client):
    active_tasks = notion_client.get_active_tasks()

    assert len(active_tasks) > 0
    assert isinstance(active_tasks, List) and all(isinstance(i, Task) for i in active_tasks)


def test_get_notion_task(notion_client):
    expected_task = Task(ticktick_id="hy76b3d2c8e60f1472064fte",
                         ticktick_etag="9durj438",
                         created_date="9999-09-09",
                         status=2,
                         title="Test Existing Task Static",
                         focus_time=0.9,
                         deleted=0,
                         tags=("test", "existing"),
                         project_id="t542b6d8e9f2de3c5d6e7f8a9s2h",
                         timezone="America/Bogota",
                         due_date="9999-09-09",
                         )

    task = notion_client.get_notion_task(expected_task)

    assert task == expected_task


def test_get_task_that_does_not_exist(notion_client):
    search_task = Task(ticktick_id="0testdoesntexisttask0",
                       ticktick_etag="0testdoesntexisttask0",
                       created_date="2099-09-09",
                       status=2,
                       title="Test Task That Does Not Exist",
                       )
    task = notion_client.get_notion_task(search_task)

    assert task is None


def test_get_task_with_missing_properties(notion_client):
    expected_task = Task(ticktick_id="tg81h23oi12h3jkh2720fu321",
                         ticktick_etag="d9iej37s",
                         created_date="2099-09-09",
                         status=2,
                         title="Test Existing Task With Missing Data",
                         )

    task = notion_client.get_notion_task(expected_task)

    assert task == expected_task


def test_get_notion_id_by_ticktick_id(notion_client):
    expected_notion_id = "f088993635c340cc8e98298ab93ed685"
    task = Task(ticktick_id="a7f9b3d2c8e60f1472065ac4",
                ticktick_etag="test-wrong-etag-f8ruej",
                created_date="2099-09-09",
                title="Test Existing Task With Missing Data",
                )

    notion_id = notion_client.get_task_notion_id(task)

    assert notion_id == expected_notion_id


def test_get_notion_id_by_etag(notion_client):
    expected_notion_id = "f088993635c340cc8e98298ab93ed685"
    task = Task(ticktick_id="test-wrong-ticktick-id-f8ruej",
                ticktick_etag="muu17zqq",
                created_date="2099-09-09",
                title="Test Existing Task With Missing Data",
                )

    notion_id = notion_client.get_task_notion_id(task)

    assert notion_id == expected_notion_id


@pytest.mark.parametrize("task_etag, expected_status", [
    # Test with a test task
    ("muu17zqq", True),

    # Test with a task that does not exist
    ("0testtask0", False),
])
def test_is_task_already_created(notion_client, task_etag, expected_status):
    is_task_created = notion_client.is_task_already_created(Task(ticktick_etag=task_etag, created_date="", title="",
                                                                 ticktick_id=""))

    assert is_task_created == expected_status


def test_create_task(notion_client):
    task_id = uuid4().hex
    expected_task = Task(ticktick_id=task_id,
                         ticktick_etag="created-task-to-delete",
                         created_date="9999-09-09",
                         status=0,
                         title="Test Task to Delete",
                         focus_time=0.9,
                         tags=("test", "existing", "delete"),
                         project_id="a123a4b5c6d7e8f9a0b1c2d3s4h",
                         timezone="America/Bogota",
                         due_date="9999-09-09",
                         )

    notion_client.create_task(expected_task)

    task = notion_client.get_notion_task(expected_task)
    assert task == expected_task

    notion_client.delete_task(expected_task)
    assert notion_client.is_task_already_created(expected_task) is False


def test_complete_task(notion_client):
    task_id = uuid4().hex
    expected_task = Task(ticktick_id=task_id,
                         ticktick_etag="complete",
                         created_date="9999-09-09",
                         status=0,
                         title="Test Task to Complete",
                         focus_time=0.9,
                         tags=("test", "existing", "complete"),
                         project_id="f9ri34b5c6f7rh29a0b1f9eo2ln",
                         timezone="America/Bogota",
                         due_date="9999-09-09",
                         )

    notion_client.create_task(expected_task)
    notion_client.complete_task(expected_task)

    task = notion_client.get_notion_task(expected_task)
    assert task.status == 2

    notion_client.delete_task(expected_task)
    assert notion_client.is_task_already_created(expected_task) is False


def test_update_task(notion_client):
    expected_task = Task(ticktick_id="a7f9b3d2c8e60f1472065ac4",
                         ticktick_etag="muu17zqq",
                         created_date="9999-09-09",
                         status=2,
                         title="Test Existing Task",
                         focus_time=random.random(),
                         tags=("test", "existing"),
                         project_id="4a72b6d8e9f2103c5d6e7f8a9b0c",
                         timezone="America/Bogota",
                         due_date="9999-09-09",
                         )

    original_task = notion_client.get_notion_task(expected_task)
    notion_client.update_task(expected_task)
    updated_task = notion_client.get_notion_task(expected_task)

    assert updated_task == expected_task
    assert updated_task.title == original_task.title
    assert updated_task.focus_time != original_task.focus_time


def test_create_task_note(notion_client):
    task_id = uuid4().hex
    expected_task = Task(ticktick_id=task_id,
                         ticktick_etag="created-task-note-to-delete",
                         created_date="9999-09-09",
                         status=0,
                         title="Test Task Note to Delete",
                         focus_time=0.9,
                         tags=("test", "existing", "delete", "unprocessed"),
                         project_id="a123a4b5c6d7e8f9a0b1c2d3s4h",
                         timezone="America/Bogota",
                         due_date="9999-09-09",
                         )

    notion_client.create_task_note(expected_task)

    task = notion_client.get_notion_task_note(expected_task)
    assert task == expected_task

    notion_client.delete_task_note(expected_task)
    assert notion_client.is_task_note_already_created(expected_task) is False


def test_complete_task_note(notion_client):
    task_id = uuid4().hex
    expected_task = Task(ticktick_id=task_id,
                         ticktick_etag="complete",
                         created_date="9999-09-09",
                         status=0,
                         title="Test Task to Complete",
                         focus_time=0.9,
                         tags=("test", "existing", "complete"),
                         project_id="f9ri34b5c6f7rh29a0b1f9eo2ln",
                         timezone="America/Bogota",
                         due_date="9999-09-09",
                         )

    notion_client.create_task_note(expected_task)
    notion_client.complete_task_note(expected_task)

    task = notion_client.get_notion_task_note(expected_task)
    assert task.status == 2

    notion_client.delete_task_note(expected_task)
    assert notion_client.is_task_note_already_created(expected_task) is False


def test_update_task_note(notion_client):
    expected_task = Task(ticktick_id="a7f9b3d2c8e60f1472065ac4",
                         ticktick_etag="muu17zqq",
                         created_date="9999-09-09",
                         status=2,
                         title="Test Existing Task",
                         focus_time=random.random(),
                         tags=("test", "existing"),
                         project_id="4a72b6d8e9f2103c5d6e7f8a9b0c",
                         timezone="America/Bogota",
                         due_date="9999-09-09",
                         )

    original_task = notion_client.get_notion_task_note(expected_task)
    notion_client.update_task_note(expected_task)
    updated_task = notion_client.get_notion_task_note(expected_task)

    assert updated_task == expected_task
    assert updated_task.title == original_task.title
    assert updated_task.focus_time != original_task.focus_time


def test_add_expense_log(notion_client):
    expected_expense_log = ExpenseLog(date="9999-09-09", expense=99.9, product="Test Expense Log")

    expense_log = notion_client.add_expense_log(expected_expense_log)

    expense_log_entry = notion_client.notion_api.get_table_entry(expense_log["id"])
    expense_log_properties = expense_log_entry["properties"]
    assert expense_log_properties[ExpensesHeaders.DATE.value]["date"]["start"] == expected_expense_log.date
    assert expense_log_properties[ExpensesHeaders.EXPENSE.value]["number"] == expected_expense_log.expense
    assert (expense_log_properties[ExpensesHeaders.PRODUCT.value]["title"][0]["text"]["content"]
            == expected_expense_log.product)

    notion_client.notion_api.update_table_entry(expense_log["id"], NotionPayloads.delete_table_entry())


def test_get_incomplete_stats_dates(notion_client):
    stats_date = datetime.now() + timedelta(days=2)

    incomplete_dates = notion_client.get_incomplete_stats_dates(stats_date)

    assert len(incomplete_dates) >= 2
    assert (isinstance(incomplete_dates, List) and
            all(datetime.strptime(i, '%Y-%m-%d') for i in incomplete_dates))


def test_update_stats_row(notion_client):
    notion_api = notion_client.notion_api
    expected_stat = PersonalStats(date="1999-09-09",
                                  weight=0,
                                  work_time=99.9,
                                  leisure_time=99.9,
                                  focus_time=random.random())

    original_stat = notion_client._parse_stats_rows(notion_api.get_table_entry("c568738e82a24b258071e5412db89a2f"))[0]
    notion_client.update_stat(expected_stat)
    updated_stat = notion_client._parse_stats_rows(notion_api.get_table_entry("c568738e82a24b258071e5412db89a2f"))[0]

    assert updated_stat == expected_stat
    assert updated_stat.date == original_stat.date
    assert updated_stat.focus_time != original_stat.focus_time


@pytest.mark.parametrize("start_date, end_date, expected_stats", [
    # Test start date before end date
    (date(2023, 1, 1), date(2023, 1, 3),
     [PersonalStats(date='2023-01-01', work_time=2.03, leisure_time=6.5, focus_time=0, weight=0),
      PersonalStats(date='2023-01-02', work_time=3.24, leisure_time=3.24, focus_time=3.12, weight=0),
      PersonalStats(date='2023-01-03', work_time=7.52, leisure_time=1.52, focus_time=6.33, weight=0)]),

    # Test start date equal to end date
    (date(2023, 1, 1), date(2023, 1, 1),
     [PersonalStats(date='2023-01-01', work_time=2.03, leisure_time=6.5, focus_time=0, weight=0)]),

    # Test start date after end date
    (date(2023, 1, 3), date(2023, 1, 1), []),
])
def test_get_stats_between_dates(notion_client, start_date, end_date, expected_stats):
    stats = notion_client.get_stats_between_dates(start_date, end_date)
    assert stats == expected_stats
