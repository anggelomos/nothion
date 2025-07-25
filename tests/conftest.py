import pytest
from tickthon import Task

from nothion import PersonalStats
from nothion._config import NT_AUTH
from nothion.data_models.expense_log import ExpenseLog

EXISTING_TEST_TASK_PAGE_ID = "f088993635c340cc8e98298ab93ed685"
EXISTING_TEST_STAT_PAGE_ID = "c568738e82a24b258071e5412db89a2f"
EXISTING_TEST_EXPENSE_LOG_PAGE_ID = "36de61f8b24c49e286bb5b0aca9740ab"
EXISTING_TEST_JOURNAL_PAGE_ID = "0323c0567dd840ea8d4868cd75a94414"
NT_TASKS_DB_ID = "19541ab983668171baf0d28b0afd4d36"
NT_NOTES_DB_ID = "4a6c0aecd6c94199bcba293d8faad842"
NT_STATS_DB_ID = "baa09f8600924192b1e9ceef4cfa70ce"
NT_EXPENSES_DB_ID = "d7d450b6f89244cbbb27fe105121d3dd"

TEST_TASK = Task(ticktick_id="60c8d7b1e9b80e0595353bc6",
                 ticktick_etag="m18s6cgr",
                 created_date="2023-08-03",
                 status=0,
                 title="Test tasks",
                 focus_time=0.1,
                 deleted=0,
                 tags=("test", "unit"),
                 project_id="5f30772022d478db3ad1a9c2",
                 timezone="America/Bogota",
                 due_date="2023-08-03",
                 )

TEST_STAT = PersonalStats(date="9999-09-09",
                          focus_total_time=1.0,
                          focus_active_time=2.0,
                          work_time=3.0,
                          leisure_time=4.0,
                          sleep_time_amount=5.0,
                          fall_asleep_time=6.0,
                          )

TEST_EXPENSE_LOG = ExpenseLog(date="9999-09-09", expense=999.9, product="Test product")


@pytest.fixture(scope="session")
def notion_info():
    return {"auth_secret": NT_AUTH}
