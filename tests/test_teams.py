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

# to run tests: pytest test_teams.py -W ignore::DeprecationWarning

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
async def test_list_chats(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    client = initialize_client
    chats = await client.teams.chat.list_chats(user=user_id)
    assert chats is not None
    assert isinstance(chats, list)

@pytest.mark.asyncio
async def test_create_chat(initialize_client):
    user_id_1 = str(os.getenv("TEST_USER_ID_1"))
    user_id_2 = str(os.getenv("TEST_USER_ID_2"))
    client = initialize_client
    chat = await client.teams.chat.create_chat(members=[user_id_1, user_id_2])
    assert chat is not None
    assert hasattr(chat, "id")

@pytest.mark.asyncio
async def test_list_messages_in_chat(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    chat_id = str(os.getenv("TEST_CHAT_ID"))
    client = initialize_client
    messages = await client.teams.chat.list_messages(user=user_id, chat_id=chat_id)
    assert messages is not None
    assert isinstance(messages, list)

@pytest.mark.asyncio
async def test_send_message_in_chat(initialize_client):
    chat_id = str(os.getenv("TEST_CHAT_ID"))
    message_content = "Hello from test_send_message_in_chat!"
    client = initialize_client
    message = await client.teams.chat.send_message(chat_id=chat_id, content=message_content)
    assert message is not None
    assert message.body.content == message_content