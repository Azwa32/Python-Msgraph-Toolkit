from unittest.mock import AsyncMock, MagicMock
import pytest

from src.python_msgraph_toolkit.services.teams.chat import ChatService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError

@pytest.fixture
def initialise_mock():
    return MagicMock()

# to test from root directory: 
# pytest tests/unit/test_teams.py

# to test all run from root directory: 
# pytest tests/unit

@pytest.mark.asyncio
async def test_list_chats(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_chats = [MagicMock(), MagicMock()]
    mock_response = MagicMock(value=mock_chats)
    mock_client.users.by_user_id.return_value.chats.get = AsyncMock(return_value=mock_response)

    result = await service.list_chats(user="user1")

    assert result == mock_chats
    mock_client.users.by_user_id.assert_called_once_with("user1")


@pytest.mark.asyncio
async def test_list_chats_empty(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_response = MagicMock(value=None)
    mock_client.users.by_user_id.return_value.chats.get = AsyncMock(return_value=mock_response)

    result = await service.list_chats(user="user1")
    assert result is None


@pytest.mark.asyncio
async def test_list_chats_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    with pytest.raises(ValidationError, match="user is required to list chats"):
        await service.list_chats()


@pytest.mark.asyncio
async def test_list_chats_api_error(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_client.users.by_user_id.return_value.chats.get = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.list_chats(user="user1")


# ─── ChatService: create_chat ───

@pytest.mark.asyncio
async def test_create_chat(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_chat = MagicMock()
    mock_client.chats.post = AsyncMock(return_value=mock_chat)

    result = await service.create_chat(members=["user1", "user2"])

    assert result is mock_chat


@pytest.mark.asyncio
async def test_create_chat_group(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_chat = MagicMock()
    mock_client.chats.post = AsyncMock(return_value=mock_chat)

    result = await service.create_chat(members=["user1", "user2", "user3"])

    assert result is mock_chat


@pytest.mark.asyncio
async def test_create_chat_too_few_members(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    with pytest.raises(ValidationError, match="At least two members are required"):
        await service.create_chat(members=["user1"])


@pytest.mark.asyncio
async def test_create_chat_no_members(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    with pytest.raises(ValidationError, match="At least two members are required"):
        await service.create_chat()


@pytest.mark.asyncio
async def test_create_chat_api_error(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_client.chats.post = AsyncMock(side_effect=Exception("server error"))

    with pytest.raises(GraphAPIError):
        await service.create_chat(members=["user1", "user2"])


# ─── ChatService: list_messages ───

@pytest.mark.asyncio
async def test_list_messages(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_messages = [MagicMock(), MagicMock()]
    mock_response = MagicMock(value=mock_messages)
    mock_client.chats.by_chat_id.return_value.messages.get = AsyncMock(return_value=mock_response)

    result = await service.list_messages(chat_id="chat1")

    assert result == mock_messages
    mock_client.chats.by_chat_id.assert_called_once_with("chat1")


@pytest.mark.asyncio
async def test_list_messages_empty(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_response = MagicMock(value=None)
    mock_client.chats.by_chat_id.return_value.messages.get = AsyncMock(return_value=mock_response)

    result = await service.list_messages(chat_id="chat1")
    assert result is None


@pytest.mark.asyncio
async def test_list_messages_missing_chat_id(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    with pytest.raises(ValidationError, match="chat_id is required"):
        await service.list_messages()


@pytest.mark.asyncio
async def test_list_messages_invalid_top(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    with pytest.raises(ValidationError, match="top must be a positive integer"):
        await service.list_messages(chat_id="chat1", top=0)


@pytest.mark.asyncio
async def test_list_messages_api_error(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_client.chats.by_chat_id.return_value.messages.get = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.list_messages(chat_id="chat1")


# ─── ChatService: send_message ───

@pytest.mark.asyncio
async def test_send_message(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_result = MagicMock()
    mock_client.chats.by_chat_id.return_value.messages.post = AsyncMock(return_value=mock_result)

    result = await service.send_message(chat_id="chat1", content="Hello!")

    assert result is mock_result
    mock_client.chats.by_chat_id.assert_called_once_with("chat1")


@pytest.mark.asyncio
async def test_send_message_missing_chat_id(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    with pytest.raises(ValidationError, match="chat_id is required"):
        await service.send_message(content="Hello!")


@pytest.mark.asyncio
async def test_send_message_missing_content(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    with pytest.raises(ValidationError, match="content is required"):
        await service.send_message(chat_id="chat1")


@pytest.mark.asyncio
async def test_send_message_api_error(initialise_mock):
    mock_client = initialise_mock
    service = ChatService(mock_client)

    mock_client.chats.by_chat_id.return_value.messages.post = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.send_message(chat_id="chat1", content="Hello!")
