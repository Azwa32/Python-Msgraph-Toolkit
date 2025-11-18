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

# to run tests: pytest test_outlook.py -W ignore::DeprecationWarning

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

@pytest.mark.asyncio
async def test_get_folder_by_name(initialize_client):
    user_email = str(os.getenv("TEST_OUTLOOK_USER_EMAIL"))
    target_folder_name = str(os.getenv("TEST_OUTLOOK_FOLDER_NAME"))
    client = initialize_client
    folder = await client.outlook.emails.get_folder_by_name(user=user_email, target_folder_name=target_folder_name)
    assert folder is not None
    assert folder.display_name == target_folder_name

@pytest.mark.asyncio
async def test_get_folder_by_name_with_parent(initialize_client):
    user_email = str(os.getenv("TEST_OUTLOOK_USER_EMAIL"))
    parent_folder_id = str(os.getenv("TEST_OUTLOOK_PARENT_FOLDER_ID"))
    target_folder_name = str(os.getenv("TEST_OUTLOOK_CHILD_FOLDER_NAME"))
    client = initialize_client
    folder = await client.outlook.emails.get_folder_by_name(
        user=user_email, 
        target_folder_name=target_folder_name,
        parent_folder_id=parent_folder_id
    )
    assert folder is not None
    assert folder.display_name == target_folder_name

@pytest.mark.asyncio
async def test_get_messages_in_folder(initialize_client):
    user_email = str(os.getenv("TEST_OUTLOOK_USER_EMAIL"))
    parent_folder_id = str(os.getenv("TEST_OUTLOOK_MESSAGES_FOLDER_ID"))
    client = initialize_client
    messages = await client.outlook.emails.get_messages_in_folder(user=user_email, parent_folder_id=parent_folder_id)
    assert messages is not None
    assert isinstance(messages, list)
    # Note: folder might be empty, so we don't assert len(messages) > 0