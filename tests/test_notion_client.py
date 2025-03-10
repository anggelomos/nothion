import random
from datetime import datetime, timedelta, date
from typing import List
from uuid import uuid4

import pytest
from nothion import NotionClient, PersonalStats
from nothion._config import NT_STATS_DB_ID, NT_NOTES_DB_ID
from tickthon import Task, ExpenseLog

from nothion._notion_payloads import NotionPayloads
from nothion._notion_table_headers import ExpensesHeaders, StatsHeaders, NotesHeaders
from tests.conftest import EXISTING_TEST_JOURNAL_PAGE_ID


@pytest.fixture(scope="module")
def notion_client(notion_info):
    return NotionClient(notion_info["auth_secret"])


def test_get_active_tasks(notion_client):
    active_tasks = notion_client.tasks.get_active_tasks()

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

    task = notion_client.tasks.get_notion_task(expected_task)

    assert task == expected_task


def test_get_task_that_does_not_exist(notion_client):
    search_task = Task(ticktick_id="0testdoesntexisttask0",
                       ticktick_etag="0testdoesntexisttask0",
                       created_date="2099-09-09",
                       status=2,
                       title="Test Task That Does Not Exist",
                       )
    task = notion_client.tasks.get_notion_task(search_task)

    assert task is None


def test_get_task_with_missing_properties(notion_client):
    expected_task = Task(ticktick_id="tg81h23oi12h3jkh2720fu321",
                         ticktick_etag="d9iej37s",
                         created_date="2099-09-09",
                         status=2,
                         title="Test Existing Task With Missing Data",
                         )

    task = notion_client.tasks.get_notion_task(expected_task)

    assert task == expected_task


def test_get_notion_id_by_ticktick_id(notion_client):
    expected_notion_id = "f088993635c340cc8e98298ab93ed685"
    task = Task(ticktick_id="a7f9b3d2c8e60f1472065ac4",
                ticktick_etag="test-wrong-etag-f8ruej",
                created_date="2099-09-09",
                title="Test Existing Task With Missing Data",
                )

    notion_id = notion_client.tasks.get_notion_id(task)

    assert notion_id == expected_notion_id


def test_get_notion_id_by_etag(notion_client):
    expected_notion_id = "f088993635c340cc8e98298ab93ed685"
    task = Task(ticktick_id="test-wrong-ticktick-id-f8ruej",
                ticktick_etag="muu17zqq",
                created_date="2099-09-09",
                title="Test Existing Task With Missing Data",
                )

    notion_id = notion_client.tasks.get_notion_id(task)

    assert notion_id == expected_notion_id


@pytest.mark.parametrize("task_etag, expected_status", [
    # Test with a test task
    ("muu17zqq", True),

    # Test with a task that does not exist
    ("0testtask0", False),
])
def test_is_task_already_created(notion_client, task_etag, expected_status):
    is_task_created = notion_client.tasks.is_already_created(Task(ticktick_etag=task_etag, created_date="", title="",
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

    notion_client.tasks.create(expected_task)

    task = notion_client.tasks.get_notion_task(expected_task)
    assert task == expected_task

    notion_client.tasks.delete(expected_task)
    assert notion_client.tasks.is_already_created(expected_task) is False


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

    task = notion_client.tasks.get_notion_task(expected_task)
    assert task.status == 2

    notion_client.tasks.delete(expected_task)
    assert notion_client.tasks.is_already_created(expected_task) is False


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

    original_task = notion_client.tasks.get_notion_task(expected_task)
    notion_client.tasks.update(expected_task)
    updated_task = notion_client.tasks.get_notion_task(expected_task)

    assert updated_task == expected_task
    assert updated_task.title == original_task.title
    assert updated_task.focus_time != original_task.focus_time


def test_create_task_note(notion_client):
    task_id = uuid4().hex
    expected_task = Task(ticktick_id=task_id,
                         column_id="test-column-id",
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

    notion_client.notes.create_task(expected_task)

    task = notion_client.notes.get_task_note(expected_task)
    assert task == expected_task

    notion_client.notes.delete_task(expected_task)
    assert notion_client.notes.is_task_already_created(expected_task) is False


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

    notion_client.notes.create_task(expected_task)
    notion_client.notes.complete_task(expected_task)

    task = notion_client.notes.get_task_note(expected_task)
    assert task.status == 2

    notion_client.notes.delete_task(expected_task)
    assert notion_client.notes.is_task_already_created(expected_task) is False


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

    original_task = notion_client.notes.get_task_note(expected_task)
    notion_client.notes.update_task(expected_task)
    updated_task = notion_client.notes.get_task_note(expected_task)

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


def test_add_highlight_log(notion_client):
    expected_highlight_log = Task(title="Tested nothion highlight", due_date="9999-09-09",
                                  ticktick_id="726db85349f01aec349fdb83", created_date=datetime.utcnow().isoformat(),
                                  ticktick_etag="3c02ab1d", tags=("highlight",))

    highlight_log = notion_client.notes.add_highlight_log(expected_highlight_log)

    highlight_log_entry = notion_client.notion_api.get_table_entry(highlight_log["id"])
    highlight_log_properties = highlight_log_entry["properties"]
    assert notion_client.notes.is_highlight_log_already_created(expected_highlight_log)
    assert highlight_log_properties[NotesHeaders.TYPE.value]["select"]["name"] in expected_highlight_log.tags
    assert (highlight_log_properties[NotesHeaders.NOTE.value]["title"][0]["text"]["content"] ==
            expected_highlight_log.title)

    highlight_date = (datetime.fromisoformat(highlight_log_properties[NotesHeaders.DUE_DATE.value]["date"]["start"])
                      .replace(tzinfo=None))
    expected_highlight_date = (datetime.fromisoformat(expected_highlight_log.created_date)
                               .replace(second=0, microsecond=0))
    assert (highlight_date == expected_highlight_date)

    notion_client.notion_api.update_table_entry(highlight_log["id"], NotionPayloads.delete_table_entry())


def test_get_incomplete_stats_dates(notion_client):
    stats_date = datetime.now() + timedelta(days=2)

    incomplete_dates = notion_client.stats.get_incomplete_dates(stats_date)

    assert len(incomplete_dates) >= 2
    assert (isinstance(incomplete_dates, List) and
            all(datetime.strptime(i, '%Y-%m-%d') for i in incomplete_dates))


def test_create_stats_row(notion_client):
    stats = PersonalStats(date="9999-09-09", work_time=1.0, sleep_time=2.0, leisure_time=3.0, focus_time=4.0,
                          weight=5.0)

    notion_client.stats.update(stats)

    date_row = notion_client.notion_api.query_table(NT_STATS_DB_ID, NotionPayloads.get_date_rows("9999-09-09"))[0]
    date_row_properties = date_row["properties"]
    assert date_row_properties[StatsHeaders.DATE.value]["date"]["start"] == stats.date
    assert date_row_properties[StatsHeaders.WORK_TIME.value]["number"] == stats.work_time
    assert date_row_properties[StatsHeaders.SLEEP_TIME.value]["number"] == stats.sleep_time
    assert date_row_properties[StatsHeaders.LEISURE_TIME.value]["number"] == stats.leisure_time
    assert date_row_properties[StatsHeaders.FOCUS_TIME.value]["number"] == stats.focus_time
    assert date_row_properties[StatsHeaders.WEIGHT.value]["number"] == stats.weight

    notion_client.notion_api.update_table_entry(date_row["id"], NotionPayloads.delete_table_entry())


def test_update_stats_row(notion_client):
    notion_api = notion_client.notion_api
    expected_stat = PersonalStats(date="1999-09-09",
                                  weight=0,
                                  work_time=99.9,
                                  leisure_time=99.9,
                                  focus_time=random.random())

    original_stat = notion_client.stats._parse_stats_rows(notion_api.get_table_entry("c568738e82a24b258071e5412db89a2f"))[0]
    notion_client.stats.update(expected_stat)
    updated_stat = notion_client.stats._parse_stats_rows(notion_api.get_table_entry("c568738e82a24b258071e5412db89a2f"))[0]

    assert updated_stat == expected_stat
    assert updated_stat.date == original_stat.date
    assert updated_stat.focus_time != original_stat.focus_time


@pytest.mark.parametrize("start_date, end_date, expected_stats", [
    # Test start date before end date
    (date(2023, 1, 1), date(2023, 1, 3),
     [PersonalStats(date='2023-01-01', work_time=2.03, leisure_time=6.5, focus_time=0, weight=0),
      PersonalStats(date='2023-01-02', work_time=3.24, leisure_time=3.24, focus_time=3.12, weight=0),
      PersonalStats(date='2023-01-03', work_time=7.57, leisure_time=1.51, focus_time=6.33, weight=0)]),

    # Test start date equal to end date
    (date(2023, 1, 1), date(2023, 1, 1),
     [PersonalStats(date='2023-01-01', work_time=2.03, leisure_time=6.5, focus_time=0, weight=0)]),

    # Test start date after end date
    (date(2023, 1, 3), date(2023, 1, 1), []),
])
def test_get_stats_between_dates(notion_client, start_date, end_date, expected_stats):
    stats = notion_client.stats.get_between_dates(start_date, end_date)
    assert stats == expected_stats


@pytest.mark.parametrize("title, page_type, expected_result", [
    # Test with a valid title and page type
    ("test-journal-entry", "journal", True),

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


def test_create_note_page(notion_client):
    note_page = ["test-note-page", "note", ("test",), datetime(2000, 1, 1),
                 "test note page content"]

    notion_client.notes.create_page(*note_page)

    note_page_payload = NotionPayloads.get_note_page(note_page[0], note_page[1])
    created_note_page = notion_client.notion_api.query_table(NT_NOTES_DB_ID, note_page_payload)[0]
    page_properties = created_note_page["properties"]

    assert page_properties[NotesHeaders.NOTE.value]["title"][0]["plain_text"] == note_page[0]
    assert page_properties[NotesHeaders.TYPE.value]["select"]["name"] == note_page[1]
    assert page_properties[NotesHeaders.SUBTYPE.value]["multi_select"][0]["name"] == note_page[2][0]
    assert page_properties[NotesHeaders.DUE_DATE.value]["date"]["start"] == note_page[3].strftime("%Y-%m-%d")

    notion_client.notion_api.update_table_entry(created_note_page["id"], NotionPayloads.delete_table_entry())


def test_get_daily_journal_data(notion_client):
    expected_object = "page"
    expected_id = EXISTING_TEST_JOURNAL_PAGE_ID

    journal_data = notion_client.notes.get_daily_journal_data(datetime(1900, 1, 1))

    assert journal_data.get("object", "") == expected_object
    assert journal_data.get("id", "").replace("-", "") == expected_id


def test_get_daily_journal_content(notion_client):
    expected_journal_content = [['test-header-1'], ['test-header-2'], ['test-header-2'], ['test-paragraph'],
                                ['- test-bullet'], ['> test-toggle']]

    journal_content = notion_client.notes.get_daily_journal_content(datetime(1900, 1, 1))

    assert len(journal_content) == len(expected_journal_content)
    assert journal_content == expected_journal_content
