import json
import random
from typing import List, Dict

import pytest

from nothion._notion_api import NotionAPI
from nothion._notion_payloads import NotionPayloads
from .conftest import (NT_TASKS_DB_ID, TEST_TASK, TEST_STAT, TEST_EXPENSE_LOG, EXISTING_TEST_TASK_PAGE_ID,
                       NT_NOTES_DB_ID, NT_STATS_DB_ID, NT_EXPENSES_DB_ID, EXISTING_TEST_STAT_PAGE_ID,
                       EXISTING_TEST_EXPENSE_LOG_PAGE_ID, EXISTING_TEST_JOURNAL_PAGE_ID)


notion_payloads = NotionPayloads(tasks_db_id=NT_TASKS_DB_ID, 
                                 notes_db_id=NT_NOTES_DB_ID, 
                                 stats_db_id=NT_STATS_DB_ID, 
                                 expenses_db_id=NT_EXPENSES_DB_ID)

@pytest.fixture(scope="module")
def notion_api(notion_info):
    return NotionAPI(notion_info["auth_secret"])


@pytest.mark.parametrize("payload", [
    # Test with tasks database
    (notion_payloads.create_task(TEST_TASK)),

    # Test with stats database
    (notion_payloads.update_stats_row(TEST_STAT, new_row=True)),

    # Test with expenses database
    (notion_payloads.create_expense_log(TEST_EXPENSE_LOG)),
])
def test_create_table_entry(notion_api, payload):
    table_entry_data = notion_api.create_table_entry(payload)

    table_entry = notion_api.get_table_entry(table_entry_data["id"])

    notion_api.update_table_entry(table_entry["id"], notion_payloads.delete_table_entry())


@pytest.mark.parametrize("database_id, query, expected_property, expected_value", [
    # Test with tasks database
    (NT_TASKS_DB_ID,
     {"filter":{"and":[{"property":"Title","title":{"equals":"Test Existing Task Static"}}]}},
     "id", "23041ab9-8366-810b-9cfe-dae0f672e9b1"),

    # Test with tasks database
    (NT_NOTES_DB_ID,
     {"filter": {"and": [{"property": "Note", "title": {"equals": "Test Existing Task"}}]}},
     "id", "c964714a-6fd8-474a-ba60-bb215c5ce77b"),

    # Test with stats database
    (NT_STATS_DB_ID,
     {"filter": {"and": [{"property": "name", "rich_text": {"equals": "Test Existing Stat"}}]}},
     "id", "c568738e-82a2-4b25-8071-e5412db89a2f"),

    # Test with expenses database
    (NT_EXPENSES_DB_ID,
     {"filter": {"and": [{"property": "item", "rich_text": {"equals": "Test Existing Expense Log"}}]}},
     "id", "36de61f8-b24c-49e2-86bb-5b0aca9740ab"),
])
def test_query_table(notion_api, database_id, query, expected_property, expected_value):
    table_entries = notion_api.query_table(database_id, query)

    assert len(table_entries) == 1
    assert table_entries[0][expected_property] == expected_value


@pytest.mark.parametrize("query, expected_pages", [
    # Test with a page limit
    ({"filter": {"and": [{"property": "año", "formula": {"number": {"equals": 2023}}},
                         {"property": "mes", "formula": {"number": {"equals": 1}}}]},
      "page_size": 10},
     10),

    # Test without a page limit
    ({"filter": {"and": [{"property": "año", "formula": {"number": {"equals": 2023}}}]}},
     361),
])
def test_query_with_multiple_pages(notion_api, query, expected_pages):
    table_entries = notion_api.query_table(NT_EXPENSES_DB_ID, query)

    assert isinstance(table_entries, List) and all(isinstance(i, Dict) for i in table_entries)
    assert len(table_entries) == expected_pages


@pytest.mark.parametrize("page_id, stable_property, updated_property, payload", [
    # Test with tasks database
    (EXISTING_TEST_TASK_PAGE_ID, "Note", "Focus time",
     json.dumps({"properties": {"Focus time": {"number": random.random()}}})),

    # Test with stats database
    (EXISTING_TEST_STAT_PAGE_ID, "ftr - focus time rescuetime", "ftw - focus time work",
     json.dumps({"properties": {"ftw - focus time work": {"number": random.random()}}})),

    # Test with expenses database
    (EXISTING_TEST_EXPENSE_LOG_PAGE_ID, "item", "expense",
     json.dumps({"properties": {"expense": {"number": random.random()}}})),
])
def test_update_table_entry(notion_api, stable_property, updated_property, page_id, payload):
    original_table_entry = notion_api.get_table_entry(page_id)

    notion_api.update_table_entry(page_id, payload)

    updated_table_entry = notion_api.get_table_entry(page_id)
    assert original_table_entry["properties"][stable_property] == updated_table_entry["properties"][stable_property]
    assert original_table_entry["properties"][updated_property] != updated_table_entry["properties"][updated_property]


def test_get_block_children(notion_api):
    expected_children = 6
    expected_first_children_type = "heading_1"
    block_children = notion_api.get_block_children(EXISTING_TEST_JOURNAL_PAGE_ID)

    assert len(block_children.get("results", [])) == expected_children
    assert block_children.get("results", [])[0].get("type", "") == expected_first_children_type
