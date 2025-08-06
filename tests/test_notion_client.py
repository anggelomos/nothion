import random
from datetime import datetime, timedelta, date
from typing import List
from uuid import uuid4

import pytest
from nothion import NotionClient, PersonalStats
from tickthon import Task

from nothion._notion_parsers import NotionParsers
from nothion._notion_payloads import NotionPayloads
from nothion._notion_table_headers import ExpensesHeaders, StatsHeaders
from nothion.data_models.expense_log import ExpenseLog
from .conftest import NT_EXPENSES_DB_ID, NT_STATS_DB_ID, NT_TASKS_DB_ID, NT_NOTES_DB_ID


@pytest.fixture(scope="module")
def notion_client(notion_info):
    return NotionClient(notion_info["auth_secret"],
                        tasks_db_id=NT_TASKS_DB_ID,
                        stats_db_id=NT_STATS_DB_ID,
                        expenses_db_id=NT_EXPENSES_DB_ID,
                        notes_db_id=NT_NOTES_DB_ID)


def test_get_active_tasks(notion_client):
    active_tasks = notion_client.tasks.get_active_tasks()

    assert len(active_tasks) > 0
    assert isinstance(active_tasks, List) and all(isinstance(i, Task) for i in active_tasks)


def test_get_task(notion_client):
    expected_task = Task(ticktick_id="",
                         ticktick_etag="",
                         created_date="2025-07-14",
                         status=0,
                         title="Test Existing Task Static",
                         focus_time=0.9,
                         deleted=0,
                         tags=tuple(["test-existing-tag"]),
                         project_id="t542b6d8e9f2de3c5d6e7f8a9s2h",
                         timezone="",
                         due_date="9999-09-09",
                         column_id="4ff69f89b28d81f38d47",
                         )

    task = notion_client.tasks.get_task(expected_task)

    assert task == expected_task


def test_get_task_that_does_not_exist(notion_client):
    search_task = Task(ticktick_id="0testdoesntexisttask0",
                       ticktick_etag="0testdoesntexisttask0",
                       created_date="2099-09-09",
                       status=2,
                       title="Test Task That Does Not Exist",
                       )
    task = notion_client.tasks.get_task(search_task)

    assert task is None


def test_get_task_with_missing_properties(notion_client):
    expected_task = Task(ticktick_id="",
                         ticktick_etag="",
                         created_date="2025-07-15",
                         status=0,
                         title="Test Existing Task With Missing Data",
                         )

    task = notion_client.tasks.get_task(expected_task)

    assert task == expected_task


@pytest.mark.parametrize("task_title, expected_status", [
    # Test with a test task
    ("Test Existing Task Static", True),

    # Test with a task that does not exist
    ("0testtask0", False),
])
def test_is_task_already_created(notion_client, task_title, expected_status):
    is_task_created = notion_client.tasks.is_task_already_created(Task(ticktick_id="", ticktick_etag="", created_date="", title=task_title))

    assert is_task_created == expected_status


@pytest.mark.xfail(reason="The task creation in notion is currently disabled, because it's syncing automatically due to the integration with ticktick."
                          "I'll keep this tests here just in case I need to re-enable it in the future.")
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

    notion_client.tasks.create(expected_task)

    task = notion_client.tasks.get_task(expected_task)
    assert task == expected_task

    notion_client.tasks.delete(expected_task)
    assert notion_client.tasks.is_already_created(expected_task) is False

@pytest.mark.xfail(reason="The task completion in notion is currently disabled, because it's syncing automatically due to the integration with ticktick."
                          "I'll keep this tests here just in case I need to re-enable it in the future.")
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

    notion_client.tasks.create(expected_task)
    notion_client.tasks.complete(expected_task)

    task = notion_client.tasks.get_task(expected_task)
    assert task.status == 2

    notion_client.tasks.delete(expected_task)
    assert notion_client.tasks.is_already_created(expected_task) is False


def test_update_task(notion_client):
    expected_task = Task(ticktick_id="",
                         ticktick_etag="",
                         created_date="2025-07-15",
                         status=0,
                         title="Test Existing Task to Update",
                         focus_time=random.random(),
                         tags=tuple(["test-existing-tag"]),
                         project_id="4a72b6d8e9f2103c5d6e7f8a9b0c",
                         column_id="4ff69f89b28d81f38d47",
                         due_date="9999-09-09",
                         )

    original_task = notion_client.tasks.get_task(expected_task)
    notion_client.tasks.update_task(expected_task)
    updated_task = notion_client.tasks.get_task(expected_task)

    assert updated_task == expected_task
    assert updated_task.title == original_task.title
    assert updated_task.focus_time != original_task.focus_time


def test_add_expense_log(notion_client):
    expected_expense_log = ExpenseLog(date="9999-09-09", expense=99.9, product="Test Expense Log")

    expense_log = notion_client.expenses.add_expense_log(expected_expense_log)

    expense_log_entry = notion_client.notion_api.get_table_entry(expense_log["id"])
    expense_log_properties = expense_log_entry["properties"]
    assert expense_log_properties[ExpensesHeaders.DATE.value]["date"]["start"] == expected_expense_log.date
    assert expense_log_properties[ExpensesHeaders.EXPENSE.value]["number"] == expected_expense_log.expense
    assert (expense_log_properties[ExpensesHeaders.PRODUCT.value]["title"][0]["text"]["content"]
            == expected_expense_log.product)

    notion_client.notion_api.update_table_entry(expense_log["id"], NotionPayloads.delete_table_entry())


def test_get_incomplete_stats_dates(notion_client):
    stats_date = datetime.now() + timedelta(days=2)

    incomplete_dates = notion_client.stats.get_incomplete_dates(stats_date)

    assert len(incomplete_dates) >= 2
    assert (isinstance(incomplete_dates, List) and
            all(datetime.strptime(i, '%Y-%m-%d') for i in incomplete_dates))


def test_create_stats_row(notion_client):
    stats = PersonalStats(date="9999-09-09", focus_total_time=1.0, focus_work_time=3.0, focus_personal_time=1.0, work_time=3.0,
                          leisure_time=4.0, sleep_time_amount=5.0, fall_asleep_time=6.0, sleep_score=7.0,
                          weight=8.0, steps=9.0, water_cups=10)

    notion_client.stats.update(stats, overwrite_stats=True)

    date_row = notion_client.notion_api.query_table(notion_client.stats_db_id, NotionPayloads.get_date_rows("9999-09-09"))[0]
    date_row_properties = date_row["properties"]
    assert date_row_properties[StatsHeaders.DATE.value]["date"]["start"] == stats.date
    assert date_row_properties[StatsHeaders.FOCUS_TOTAL_TIME.value]["number"] == stats.focus_total_time
    assert date_row_properties[StatsHeaders.FOCUS_PERSONAL_TIME.value]["number"] == stats.focus_personal_time
    assert date_row_properties[StatsHeaders.FOCUS_WORK_TIME.value]["number"] == stats.focus_work_time
    assert date_row_properties[StatsHeaders.WORK_TIME.value]["number"] == stats.work_time
    assert date_row_properties[StatsHeaders.LEISURE_TIME.value]["number"] == stats.leisure_time
    assert date_row_properties[StatsHeaders.SLEEP_TIME_AMOUNT.value]["number"] == stats.sleep_time_amount
    assert date_row_properties[StatsHeaders.SLEEP_DEEP_AMOUNT.value]["number"] == stats.sleep_deep_amount
    assert date_row_properties[StatsHeaders.FALL_ASLEEP_TIME.value]["number"] == stats.fall_asleep_time
    assert date_row_properties[StatsHeaders.SLEEP_SCORE.value]["number"] == stats.sleep_score
    assert date_row_properties[StatsHeaders.WEIGHT.value]["number"] == stats.weight
    assert date_row_properties[StatsHeaders.STEPS.value]["number"] == stats.steps
    assert date_row_properties[StatsHeaders.WATER_CUPS.value]["number"] == stats.water_cups


    notion_client.notion_api.update_table_entry(date_row["id"], NotionPayloads.delete_table_entry())


def test_update_stats_row(notion_client):
    notion_api = notion_client.notion_api
    expected_stat = PersonalStats(date="1999-09-09",
                                  focus_total_time=random.random(),
                                  focus_personal_time=4.5,
                                  focus_work_time=5.5,
                                  work_time=1.2,
                                  fall_asleep_time=3,
                                  sleep_time_amount=4,
                                  sleep_score=89,
                                  leisure_time=3.4,
                                  weight=70.0,
                                  steps=1231,
                                  water_cups=8,
                                  )

    original_stat = NotionParsers.parse_stats_rows([notion_api.get_table_entry("c568738e82a24b258071e5412db89a2f")])[0]
    notion_client.stats.update(expected_stat, overwrite_stats=True)
    updated_stat = NotionParsers.parse_stats_rows([notion_api.get_table_entry("c568738e82a24b258071e5412db89a2f")])[0]

    assert updated_stat == expected_stat
    assert updated_stat.date == original_stat.date
    assert updated_stat.focus_total_time != original_stat.focus_total_time


@pytest.mark.parametrize("start_date, end_date, expected_stats", [
    # Test start date before end date
    (date(2023, 1, 1), date(2023, 1, 3),
     [PersonalStats(date='2023-01-01', work_time=2.03, leisure_time=6.5, focus_total_time=0, focus_work_time=1.97, focus_personal_time=1.23, weight=0, water_cups=0),
      PersonalStats(date='2023-01-02', work_time=3.24, leisure_time=3.24, focus_total_time=3.12, focus_work_time=3.12, focus_personal_time=0.45, weight=0, water_cups=0),
      PersonalStats(date='2023-01-03', work_time=7.57, leisure_time=1.51, focus_total_time=6.33, focus_work_time=7.42, focus_personal_time=2.07, weight=0, water_cups=0)]),

    # Test start date equal to end date
    (date(2023, 1, 1), date(2023, 1, 1),
     [PersonalStats(date='2023-01-01', work_time=2.03, leisure_time=6.5, focus_total_time=0, focus_work_time=1.97, focus_personal_time=1.23, weight=0, water_cups=0)]),

    # Test start date after end date
    (date(2023, 1, 3), date(2023, 1, 1), []),
])
def test_get_stats_between_dates(notion_client, start_date, end_date, expected_stats):
    stats = notion_client.stats.get_between_dates(start_date, end_date)
    assert stats == expected_stats


@pytest.mark.parametrize("title, page_type, expected_result", [
    # Test with a valid title and page type
    ("test-page-entry", "note", True),

    # Test with a valid title and a wrong page type
    ("test-journal-entry", "test-wrong-page-type", False),

    # Test with a wrong title and a valid page type
    ("test-wrong-title", "journal", False),

    # Test with a wrong title and page type
    ("test-wrong-title", "test-wrong-page-type", False),
])
def test_is_note_page_already_created(notion_client, title, page_type, expected_result):
    is_note_page_created = notion_client.notes.is_page_already_created(title, page_type)
    assert is_note_page_created == expected_result
