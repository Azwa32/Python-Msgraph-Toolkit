import pytest
from unittest.mock import AsyncMock, MagicMock

from src.python_msgraph_toolkit.services.teams.chat import ChatService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError


class TestChatServiceInit:
    def test_init_with_valid_client(self, mock_graph_client):
        service = ChatService(mock_graph_client)
        assert service._msgraph_client is mock_graph_client

    def test_init_with_none_client_raises(self):
        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            ChatService(None)


class TestListChats:
    @pytest.fixture
    def chat_service(self, mock_graph_client):
        return ChatService(mock_graph_client)

    async def test_missing_user_raises(self, chat_service):
        with pytest.raises(ValidationError, match="user is required"):
            await chat_service.list_chats()

    async def test_successful_list(self, chat_service, mock_graph_client):
        chats = [MagicMock(id="chat1"), MagicMock(id="chat2")]
        mock_response = MagicMock(value=chats)
        mock_graph_client.users.by_user_id.return_value.chats.get = AsyncMock(return_value=mock_response)

        result = await chat_service.list_chats(user="user123")
        assert result == chats

    async def test_empty_result_returns_none(self, chat_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.users.by_user_id.return_value.chats.get = AsyncMock(return_value=mock_response)

        result = await chat_service.list_chats(user="user123")
        assert result is None

    async def test_api_error_raises(self, chat_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.chats.get = AsyncMock(
            side_effect=Exception("chat error")
        )
        with pytest.raises(GraphAPIError):
            await chat_service.list_chats(user="user123")


class TestCreateChat:
    @pytest.fixture
    def chat_service(self, mock_graph_client):
        return ChatService(mock_graph_client)

    async def test_too_few_members_raises(self, chat_service):
        with pytest.raises(ValidationError, match="At least two members are required"):
            await chat_service.create_chat(members=["user1"])

    async def test_no_members_raises(self, chat_service):
        with pytest.raises(ValidationError, match="At least two members are required"):
            await chat_service.create_chat(members=[])

    async def test_default_no_members_raises(self, chat_service):
        with pytest.raises(ValidationError, match="At least two members are required"):
            await chat_service.create_chat()

    async def test_successful_one_on_one_create(self, chat_service, mock_graph_client):
        mock_chat = MagicMock(id="new_chat")
        mock_graph_client.chats.post = AsyncMock(return_value=mock_chat)

        result = await chat_service.create_chat(members=["user1", "user2"])
        assert result is mock_chat
        mock_graph_client.chats.post.assert_awaited_once()

    async def test_successful_group_create(self, chat_service, mock_graph_client):
        mock_chat = MagicMock(id="group_chat")
        mock_graph_client.chats.post = AsyncMock(return_value=mock_chat)

        result = await chat_service.create_chat(members=["user1", "user2", "user3"])
        assert result is mock_chat

    async def test_api_error_raises(self, chat_service, mock_graph_client):
        mock_graph_client.chats.post = AsyncMock(side_effect=Exception("create failed"))

        with pytest.raises(GraphAPIError):
            await chat_service.create_chat(members=["user1", "user2"])


class TestListMessages:
    @pytest.fixture
    def chat_service(self, mock_graph_client):
        return ChatService(mock_graph_client)

    async def test_missing_chat_id_raises(self, chat_service):
        with pytest.raises(ValidationError, match="chat_id is required"):
            await chat_service.list_messages()

    async def test_invalid_top_raises(self, chat_service):
        with pytest.raises(ValidationError, match="top must be a positive integer"):
            await chat_service.list_messages(chat_id="chat1", top=0)

    async def test_negative_top_raises(self, chat_service):
        with pytest.raises(ValidationError, match="top must be a positive integer"):
            await chat_service.list_messages(chat_id="chat1", top=-5)

    async def test_successful_list_messages(self, chat_service, mock_graph_client):
        messages = [MagicMock(id="msg1"), MagicMock(id="msg2")]
        mock_response = MagicMock(value=messages)
        mock_graph_client.chats.by_chat_id.return_value \
            .messages.get = AsyncMock(return_value=mock_response)

        result = await chat_service.list_messages(chat_id="chat1", top=5)
        assert result == messages

    async def test_no_messages_returns_none(self, chat_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.chats.by_chat_id.return_value \
            .messages.get = AsyncMock(return_value=mock_response)

        result = await chat_service.list_messages(chat_id="chat1")
        assert result is None


class TestSendMessage:
    @pytest.fixture
    def chat_service(self, mock_graph_client):
        return ChatService(mock_graph_client)

    async def test_missing_chat_id_raises(self, chat_service):
        with pytest.raises(ValidationError, match="chat_id is required"):
            await chat_service.send_message(content="Hello")

    async def test_missing_content_raises(self, chat_service):
        with pytest.raises(ValidationError, match="content is required"):
            await chat_service.send_message(chat_id="chat1")

    async def test_successful_send(self, chat_service, mock_graph_client):
        mock_msg = MagicMock(id="sent_msg")
        mock_graph_client.chats.by_chat_id.return_value \
            .messages.post = AsyncMock(return_value=mock_msg)

        result = await chat_service.send_message(chat_id="chat1", content="Hello team!")
        assert result is mock_msg

    async def test_api_error_raises(self, chat_service, mock_graph_client):
        mock_graph_client.chats.by_chat_id.return_value \
            .messages.post = AsyncMock(side_effect=Exception("send failed"))

        with pytest.raises(GraphAPIError):
            await chat_service.send_message(chat_id="chat1", content="Hello")
