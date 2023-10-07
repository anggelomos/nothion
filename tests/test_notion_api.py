import json
import random
from typing import List, Dict

import pytest
from nothion._config import NT_TASKS_DB_ID, NT_STATS_DB_ID, NT_EXPENSES_DB_ID

from nothion._notion_api import NotionAPI
from nothion._notion_payloads import NotionPayloads
from .conftest import TEST_TASK, TEST_STAT, TEST_EXPENSE_LOG, EXISTING_TEST_TASK_PAGE_ID, EXISTING_TEST_STAT_PAGE_ID, \
    EXISTING_TEST_EXPENSE_LOG_PAGE_ID


@pytest.fixture(scope="module")
def notion_api(notion_info):
    return NotionAPI(notion_info["auth_secret"])


@pytest.mark.parametrize("payload", [
    # Test with tasks database
    (NotionPayloads.create_task(TEST_TASK)),

    # Test with stats database
    (NotionPayloads.create_stat_row(TEST_STAT)),

    # Test with expenses database
    (NotionPayloads.create_expense_log(TEST_EXPENSE_LOG)),
])
def test_create_table_entry(notion_api, payload):
    table_entry_data = notion_api.create_table_entry(payload)

    table_entry = notion_api.get_table_entry(table_entry_data["id"])

    notion_api.update_table_entry(table_entry["id"], NotionPayloads.delete_table_entry())


@pytest.mark.parametrize("database_id, query, expected_property, expected_value", [
    # Test with tasks database
    (NT_TASKS_DB_ID,
     {"filter": {"and": [{"property": "Ticktick id", "rich_text": {"equals": "a7f9b3d2c8e60f1472065ac4"}}]}},
     "id", "f0889936-35c3-40cc-8e98-298ab93ed685"),

    # Test with stats database
    (NT_STATS_DB_ID,
     {"filter": {"and": [{"property": "name", "rich_text": {"equals": "Test Existing Stat"}}]}},
     "id", "c568738e-82a2-4b25-8071-e5412db89a2f"),

    # Test with expenses database
    (NT_EXPENSES_DB_ID,
     {"filter": {"and": [{"property": "producto", "rich_text": {"equals": "Test Existing Expense Log"}}]}},
     "id", "36de61f8-b24c-49e2-86bb-5b0aca9740ab"),
])
def test_query_table(notion_api, database_id, query, expected_property, expected_value):
    table_entries = notion_api.query_table(database_id, query)

    assert len(table_entries) == 1
    assert table_entries[0][expected_property] == expected_value


def test_query_with_multiple_pages(notion_api):
    query = {"filter": {"and": [{"property": "año", "formula": {"number": {"equals": 2023}}},
                                {"property": "mes", "formula": {"number": {"equals": 1}}}]},
             "page_size": 10}

    table_entries = notion_api.query_table(NT_EXPENSES_DB_ID, query)

    assert isinstance(table_entries, List) and all(isinstance(i, Dict) for i in table_entries)
    assert len(table_entries) == 37


@pytest.mark.parametrize("page_id, stable_property, updated_property, payload", [
    # Test with tasks database
    (EXISTING_TEST_TASK_PAGE_ID, "Task", "Focus time",
     json.dumps({"properties": {"Focus time": {"number": random.random()}}})),

    # Test with stats database
    (EXISTING_TEST_STAT_PAGE_ID, "work time", "focus time",
     json.dumps({"properties": {"focus time": {"number": random.random()}}})),

    # Test with expenses database
    (EXISTING_TEST_EXPENSE_LOG_PAGE_ID, "producto", "egresos",
     json.dumps({"properties": {"egresos": {"number": random.random()}}})),
])
def test_update_table_entry(notion_api, stable_property, updated_property, page_id, payload):
    original_table_entry = notion_api.get_table_entry(page_id)

    notion_api.update_table_entry(page_id, payload)

    updated_table_entry = notion_api.get_table_entry(page_id)
    assert original_table_entry["properties"][stable_property] == updated_table_entry["properties"][stable_property]
    assert original_table_entry["properties"][updated_property] != updated_table_entry["properties"][updated_property]
