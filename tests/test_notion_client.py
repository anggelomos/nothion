import pytest


@pytest.fixture(scope="module")
def notion_client(notion_info):
    return NotionClient(notion_info["auth_secret"])


def test_get_active_tasks(notion_client):
    # Get active tasks from the tasks database
    # Asserts the response is not empty
    # Asserts the response is a list of Tasks
    assert True


def test_get_task_by_id(notion_client):
    # Set the expected test task

    # Get a test task by id from the tasks database

    # Asserts the response is equal to the expected test task
    assert True


def test_get_notion_id(notion_client):
    # Set the expected notion id

    # Get the notion id of a test task by id from the tasks database

    # Asserts the response is equal to the expected notion id
    assert True


@pytest.mark.parametrize("task_id, expected_status", [
    # Test with a test task
    ({"name": "Test Task"}, True),

    # Test with a task that does not exist
    ({"name": "Test Task"}, False),
])
def test_is_task_already_created(task_id, expected_status, notion_client):
    # Set the expected test task

    # Check if a test task is already created in the tasks database

    # Asserts the response is equal to the expected test task
    assert True


def test_create_task(notion_client):
    # Set the expected task

    # Create a test task in the tasks database

    # Get the test task by id
    # Asserts the response is equal to the expected test task
    # Delete the task
    assert True


def test_update_task(notion_client):
    # Get the test task id

    # Update a test task in the tasks database

    # Get the test task by id
    # Asserts all the parameters that were not updated are equal to the expected test task
    # Asserts the updated parameters are different to the expected updated test task
    assert True


def test_add_expense_log(notion_client):
    # Set the expected expense log data

    # Add an expense log to a test task in the tasks database

    # Get the entry by id
    # Asserts the response is equal to the expected test task
    # Delete the expense log
    assert True


def test_get_incomplete_stats_dates(notion_client):
    # Set dates two days in the future

    # Get incomplete stats dates from the stats database

    # Asserts the response is equal or greater than two
    # Asserts the response is a list of dates (strings)
    assert True


def test_update_stats_row(notion_client):
    # Get the test stats row id

    # Update a test stats row in the stats database

    # Get the test stats row by id
    # Asserts all the parameters that were not updated are equal to the expected test stats row
    # Asserts the updated parameters are different to the expected updated test stats row
    assert True


@pytest.mark.parametrize("start_date, end_date, expected_data", [
    # Test start date before end date
    ("name", "Test Task", []),

    # Test start date equal to end date
    ("name", "Test Task", []),

    # Test start date after end date
    ("name", "Test Task", []),
])
def test_get_stats_between_dates(notion_client):
    # Set the expected test task

    # Get a test task by id from the tasks database

    # Asserts the response is equal to the expected test task
    assert True
