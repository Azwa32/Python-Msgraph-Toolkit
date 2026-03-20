from dotenv import load_dotenv
from pathlib import Path
import sys
import os
import pytest

# Add src/ to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from src.python_msgraph_toolkit.client import GraphClient

# to run tests: pytest test_users.py -W ignore::DeprecationWarning
# to run a single test from root folder (with print -s) eg: 
# pytest tests/test_users.py::test_list_users -s -W ignore::DeprecationWarning

@pytest.fixture
def initialize_client():
    load_dotenv()
    client = GraphClient(
        str(os.getenv("MSGRAPH_TENANT_ID")),
        str(os.getenv("MSGRAPH_CLIENT_ID")),
        str(os.getenv("MSGRAPH_API_KEY"))
        )
    return client

@pytest.mark.asyncio
async def test_list_users(initialize_client):
    client = initialize_client
    users = await client.users.users.list_users()
    if users:
        print("\n")
        for user in users:
            print(f"User Name: {user.display_name}, User Email: {user.mail}, User ID: {user.id}")
    assert users is not None
    assert isinstance(users, list)
    assert len(users) > 0

@pytest.mark.asyncio
async def test_get_user(initialize_client):
    test_user_id = str(os.getenv("TEST_USER_ID"))
    client = initialize_client
    user = await client.users.users.get_user(user_id=test_user_id)
    if user:
        print(f"User Name: {user.display_name}, User Email: {user.mail}, User ID: {user.id}")
    assert user is not None
    assert user.id == test_user_id

@pytest.mark.asyncio
async def test_get_user_by_email(initialize_client):
    test_user_email = str(os.getenv("TEST_USER_EMAIL"))
    client = initialize_client
    user = await client.users.users.get_user_by_email(email=test_user_email)
    if user:
        print(f"User Name: {user.display_name}, User Email: {user.mail}, User ID: {user.id}")
    assert user is not None
    assert user.mail == test_user_email