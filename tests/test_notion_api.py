import pytest


@pytest.fixture(scope="module")
def notion_api(notion_info):
    return NotionAPI(notion_info["auth_secret"])


@pytest.mark.parametrize("payload, database_type", [
    # Test with tasks database
    ({"name": "Test Task"}, "tasks_db"),

    # Test with stats database
    ({"name": "Test Stat"}, "stats_db"),

    # Test with expenses database
    ({"name": "Test Expense"}, "expenses_db")
])
def test_create_table_entry(payload, database_type):
    # Create table entry based on the payload
    # Asserts the entry was created using a query
    # Remove the entry id from the database
    assert True


@pytest.mark.parametrize("payload, database_type", [
    # Test with tasks database
    ({"name": "Test Task"}, "tasks_db"),

    # Test with stats database
    ({"name": "Test Stat"}, "stats_db"),

    # Test with expenses database
    ({"name": "Test Expense"}, "expenses_db")
])
def test_update_table_entry(payload, database_type):
    # Retrieve the entry id from pytest
    # Update the entry based on the payload
    # Asserts the entry was updated using a query
    assert True
