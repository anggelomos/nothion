import os

import pytest


@pytest.fixture(scope="module")
def notion_info():
    return {"auth_secret": os.getenv("NT_AUTH")}
