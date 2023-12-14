import pytest
from tickthon import Task, ExpenseLog

from nothion import PersonalStats
from nothion._config import NT_AUTH

EXISTING_TEST_TASK_PAGE_ID = "f088993635c340cc8e98298ab93ed685"
EXISTING_TEST_TASK_NOTE_PAGE_ID = "c964714a6fd8474aba60bb215c5ce77b"
EXISTING_TEST_STAT_PAGE_ID = "c568738e82a24b258071e5412db89a2f"
EXISTING_TEST_EXPENSE_LOG_PAGE_ID = "36de61f8b24c49e286bb5b0aca9740ab"

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
                          work_time=1.0,
                          leisure_time=2.0,
                          focus_time=3.0,
                          weight=0.0)

TEST_EXPENSE_LOG = ExpenseLog(date="9999-09-09", expense=999.9, product="Test product")


@pytest.fixture(scope="session")
def notion_info():
    return {"auth_secret": NT_AUTH}
