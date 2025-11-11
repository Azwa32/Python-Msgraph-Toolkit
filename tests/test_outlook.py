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

# to run tests: pytest sharepoint.py -W ignore::DeprecationWarning

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
async def test_list_root_mail_folders(initialize_client):
    user_email = str(os.getenv("TEST_OUTLOOK_USER_EMAIL"))
    client = initialize_client
    folders = await client.outlook.emails.list_root_mail_folders(user=user_email)
    assert folders is not None
    assert isinstance(folders, list)
    assert len(folders) > 0

@pytest.mark.asyncio
async def test_list_child_folders(initialize_client):
    user_email = str(os.getenv("TEST_OUTLOOK_USER_EMAIL"))
    parent_folder_id = str(os.getenv("TEST_OUTLOOK_PARENT_FOLDER_ID"))
    client = initialize_client
    child_folders = await client.outlook.emails.list_child_folders(user=user_email, folder_id=parent_folder_id)
    assert child_folders is not None
    assert isinstance(child_folders, list)
    assert len(child_folders) > 0