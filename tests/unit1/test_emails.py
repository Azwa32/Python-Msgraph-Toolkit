import pytest
from unittest.mock import AsyncMock, MagicMock

from src.python_msgraph_toolkit.services.outlook.emails import EmailsService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError


class TestEmailsServiceInit:
    def test_init_with_valid_client(self, mock_graph_client):
        service = EmailsService(mock_graph_client)
        assert service._msgraph_client is mock_graph_client

    def test_init_with_none_client_raises(self):
        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            EmailsService(None)


class TestListRootMailFolders:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_user_raises(self, email_service):
        with pytest.raises(ValidationError, match="User is required"):
            await email_service.list_root_mail_folders()

    async def test_successful_list(self, email_service, mock_graph_client):
        folders = [MagicMock(display_name="Inbox"), MagicMock(display_name="Sent")]
        mock_response = MagicMock(value=folders)
        mock_graph_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=mock_response)

        result = await email_service.list_root_mail_folders(user="user@test.com")
        assert result == folders

    async def test_none_result_returns_none(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=None)

        result = await email_service.list_root_mail_folders(user="user@test.com")
        assert result is None

    async def test_api_error_raises(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(
            side_effect=Exception("server error")
        )
        with pytest.raises(GraphAPIError):
            await email_service.list_root_mail_folders(user="user@test.com")


class TestListChildFolders:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_user_raises(self, email_service):
        with pytest.raises(ValidationError, match="User is required"):
            await email_service.list_child_folders(folder_id="folder1")

    async def test_missing_folder_id_raises(self, email_service):
        with pytest.raises(ValidationError, match="Mail folder ID is required"):
            await email_service.list_child_folders(user="user@test.com")

    async def test_successful_list(self, email_service, mock_graph_client):
        child_folders = [MagicMock(display_name="SubFolder")]
        mock_response = MagicMock(value=child_folders)
        mock_graph_client.users.by_user_id.return_value \
            .mail_folders.by_mail_folder_id.return_value \
            .child_folders.get = AsyncMock(return_value=mock_response)

        result = await email_service.list_child_folders(user="user@test.com", folder_id="inbox")
        assert result == child_folders


class TestGetFolderByName:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_user_raises(self, email_service):
        with pytest.raises(ValidationError, match="User is required"):
            await email_service.get_folder_by_name(target_folder_name="Inbox")

    async def test_missing_folder_name_raises(self, email_service):
        with pytest.raises(ValidationError, match="Folder name is required"):
            await email_service.get_folder_by_name(user="user@test.com")

    async def test_find_root_folder_by_name(self, email_service, mock_graph_client):
        inbox = MagicMock(display_name="Inbox")
        sent = MagicMock(display_name="Sent Items")
        mock_response = MagicMock(value=[inbox, sent])
        mock_graph_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=mock_response)

        result = await email_service.get_folder_by_name(user="user@test.com", target_folder_name="Inbox")
        assert result is inbox

    async def test_folder_not_found_returns_none(self, email_service, mock_graph_client):
        inbox = MagicMock(display_name="Inbox")
        mock_response = MagicMock(value=[inbox])
        mock_graph_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=mock_response)

        result = await email_service.get_folder_by_name(user="user@test.com", target_folder_name="NonExistent")
        assert result is None

    async def test_find_child_folder_by_name(self, email_service, mock_graph_client):
        subfolder = MagicMock(display_name="Archive")
        mock_response = MagicMock(value=[subfolder])
        mock_graph_client.users.by_user_id.return_value \
            .mail_folders.by_mail_folder_id.return_value \
            .child_folders.get = AsyncMock(return_value=mock_response)

        result = await email_service.get_folder_by_name(
            user="user@test.com", target_folder_name="Archive", parent_folder_id="inbox_id"
        )
        assert result is subfolder


class TestGetMessagesInFolder:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_user_raises(self, email_service):
        with pytest.raises(ValidationError, match="User is required"):
            await email_service.get_messages_in_folder(parent_folder_id="f1")

    async def test_missing_folder_id_raises(self, email_service):
        with pytest.raises(ValidationError, match="Mail folder ID is required"):
            await email_service.get_messages_in_folder(user="user@test.com")

    async def test_successful_get_messages(self, email_service, mock_graph_client):
        messages = [MagicMock(subject="Hello"), MagicMock(subject="World")]
        mock_response = MagicMock(value=messages)
        mock_graph_client.users.by_user_id.return_value \
            .mail_folders.by_mail_folder_id.return_value \
            .messages.get = AsyncMock(return_value=mock_response)

        result = await email_service.get_messages_in_folder(user="user@test.com", parent_folder_id="inbox")
        assert result == messages


class TestSendEmail:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_sender_raises(self, email_service):
        with pytest.raises(ValidationError, match="Sender is required"):
            await email_service.send(to_recipients=["a@b.com"])

    async def test_missing_recipients_raises(self, email_service):
        with pytest.raises(ValidationError, match="At least one recipient is required"):
            await email_service.send(sender="me@test.com")

    async def test_empty_recipients_raises(self, email_service):
        with pytest.raises(ValidationError, match="At least one recipient is required"):
            await email_service.send(sender="me@test.com", to_recipients=[])

    async def test_successful_send(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.send_mail.post = AsyncMock()

        result = await email_service.send(
            sender="me@test.com",
            to_recipients=["you@test.com"],
            subject="Test",
            body="Hello",
        )
        assert result is True
        mock_graph_client.users.by_user_id.return_value.send_mail.post.assert_awaited_once()

    async def test_send_api_error_raises(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.send_mail.post = AsyncMock(
            side_effect=Exception("send failed")
        )
        with pytest.raises(GraphAPIError):
            await email_service.send(sender="me@test.com", to_recipients=["you@test.com"])


class TestReply:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_sender_raises(self, email_service):
        with pytest.raises(ValidationError, match="Sender is required"):
            await email_service.reply(message_id="msg1")

    async def test_missing_message_id_raises(self, email_service):
        with pytest.raises(ValidationError, match="Message Id is required"):
            await email_service.reply(sender="me@test.com")

    async def test_successful_reply(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .messages.by_message_id.return_value \
            .reply.post = AsyncMock()

        result = await email_service.reply(sender="me@test.com", message_id="msg1", comment="Thanks")
        assert result is True


class TestReplyAll:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_sender_raises(self, email_service):
        with pytest.raises(ValidationError, match="Sender is required"):
            await email_service.reply_all(message_id="msg1")

    async def test_missing_message_id_raises(self, email_service):
        with pytest.raises(ValidationError, match="Message Id is required"):
            await email_service.reply_all(sender="me@test.com")

    async def test_successful_reply_all(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .messages.by_message_id.return_value \
            .reply_all.post = AsyncMock()

        result = await email_service.reply_all(sender="me@test.com", message_id="msg1")
        assert result is True


class TestForward:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_sender_raises(self, email_service):
        with pytest.raises(ValidationError, match="Sender is required"):
            await email_service.forward(message_id="msg1", to_recipients=["a@b.com"])

    async def test_missing_message_id_raises(self, email_service):
        with pytest.raises(ValidationError, match="Message Id is required"):
            await email_service.forward(sender="me@test.com", to_recipients=["a@b.com"])

    async def test_missing_recipients_raises(self, email_service):
        with pytest.raises(ValidationError, match="At least one recipient is required"):
            await email_service.forward(sender="me@test.com", message_id="msg1")

    async def test_successful_forward(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .messages.by_message_id.return_value \
            .forward.post = AsyncMock()

        result = await email_service.forward(
            sender="me@test.com", message_id="msg1", to_recipients=["other@test.com"]
        )
        assert result is True


class TestDeleteEmail:
    @pytest.fixture
    def email_service(self, mock_graph_client):
        return EmailsService(mock_graph_client)

    async def test_missing_user_raises(self, email_service):
        with pytest.raises(ValidationError, match="User is required"):
            await email_service.delete(message_id="msg1")

    async def test_missing_message_id_raises(self, email_service):
        with pytest.raises(ValidationError, match="Message Id is required"):
            await email_service.delete(user="user@test.com")

    async def test_successful_delete(self, email_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .messages.by_message_id.return_value \
            .delete = AsyncMock()

        result = await email_service.delete(user="user@test.com", message_id="msg1")
        assert result is True
