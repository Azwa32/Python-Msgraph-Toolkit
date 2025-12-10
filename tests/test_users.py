import warnings
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

# Now import after sys.path is configured
from msgraph_api.client import GraphClient

# to run tests: pytest test_users.py -W ignore::DeprecationWarning

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
async def test_get_user(initialize_client):
    test_user_id = str(os.getenv("TEST_USER_ID"))
    client = initialize_client
    user = await client.users.users.get_user(user_id=test_user_id)
    assert user is not None
    assert user.id == test_user_id

@pytest.mark.asyncio
async def test_list_users(initialize_client):
    client = initialize_client
    users = await client.users.users.list_users()
    assert users is not None
    assert isinstance(users, list)
    assert len(users) > 0

@pytest.mark.asyncio
async def test_get_user_by_email(initialize_client):
    test_user_email = str(os.getenv("TEST_USER_EMAIL"))
    client = initialize_client
    user = await client.users.users.get_user_by_email(email=test_user_email)
    assert user is not None
    assert user.mail == test_user_email