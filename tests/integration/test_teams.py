from dotenv import load_dotenv
import os
import pytest
from src.python_msgraph_toolkit.client import GraphClient

# to run tests from root folder: 
# pytest tests/integration/test_teams.py -W ignore::DeprecationWarning

# to run a single test from root folder (with print -s) eg: 
# pytest tests/integration/test_teams.py::test_list_chats -s -W ignore::DeprecationWarning

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
async def test_list_chats(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    client = initialize_client
    chats = await client.teams.chat.list_chats(user=user_id)
    if chats:
        print("\n")
        for chat in chats:
            print(f" Chat Topic: {chat.topic}, Chat ID: {chat.id}")
    assert chats is not None
    assert isinstance(chats, list)

@pytest.mark.asyncio
async def test_create_chat(initialize_client):
    user_id_1 = str(os.getenv("TEST_USER_ID_1"))
    user_id_2 = str(os.getenv("TEST_USER_ID_2"))
    client = initialize_client
    chat = await client.teams.chat.create_chat(members=[user_id_1, user_id_2])
    if chat:
        print(f"\nCreated Chat ID: {chat.id}")
    assert chat is not None
    assert hasattr(chat, "id")

@pytest.mark.asyncio
async def test_list_messages_in_chat(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    chat_id = str(os.getenv("TEST_CHAT_ID"))
    client = initialize_client
    messages = await client.teams.chat.list_messages(user=user_id, chat_id=chat_id)
    if messages:
        print("\n")
        for message in messages:
            print(f"Content: {message.body.content}")
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