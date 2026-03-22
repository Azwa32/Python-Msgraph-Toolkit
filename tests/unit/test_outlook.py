from unittest.mock import AsyncMock, MagicMock
import pytest

from src.python_msgraph_toolkit.services.outlook.calendar import CalendarService
from src.python_msgraph_toolkit.services.outlook.emails import EmailsService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError

@pytest.fixture
def initialise_mock():
    return MagicMock()

# to test from root directory: 
# pytest tests/unit/test_outlook.py

# to test all run from root directory: 
# pytest tests/unit

@pytest.mark.asyncio
async def test_get_events_no_date_range(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_events = [MagicMock(), MagicMock()]
    mock_response = MagicMock(value=mock_events)
    mock_client.users.by_user_id.return_value.calendar.events.get = AsyncMock(return_value=mock_response)

    result = await service.get_events(user="user1")

    assert result == mock_events
    mock_client.users.by_user_id.assert_called_once_with("user1")


@pytest.mark.asyncio
async def test_get_events_with_date_range(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_events = [MagicMock()]
    mock_response = MagicMock(value=mock_events)
    mock_client.users.by_user_id.return_value.calendar.events.get = AsyncMock(return_value=mock_response)

    result = await service.get_events(user="user1", start_date="2026-01-01T00:00:00Z", end_date="2026-12-31T23:59:59Z")

    assert result == mock_events
    mock_client.users.by_user_id.assert_called_once_with("user1")


@pytest.mark.asyncio
async def test_get_events_empty(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_response = MagicMock(value=None)
    mock_client.users.by_user_id.return_value.calendar.events.get = AsyncMock(return_value=mock_response)

    result = await service.get_events(user="user1")
    assert result is None


@pytest.mark.asyncio
async def test_get_events_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(GraphAPIError):
        await service.get_events()


@pytest.mark.asyncio
async def test_get_events_api_error(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_client.users.by_user_id.return_value.calendar.events.get = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.get_events(user="user1")


# ─── CalendarService: create_event ───

@pytest.mark.asyncio
async def test_create_event(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_event = MagicMock()
    mock_client.users.by_user_id.return_value.calendar.events.post = AsyncMock(return_value=mock_event)

    result = await service.create_event(
        user="user1", subject="Meeting", start="2026-03-22T10:00:00Z", end="2026-03-22T11:00:00Z"
    )

    assert result is mock_event
    mock_client.users.by_user_id.assert_called_once_with("user1")


@pytest.mark.asyncio
async def test_create_event_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.create_event(subject="Meeting", start="2026-03-22T10:00:00Z", end="2026-03-22T11:00:00Z")


@pytest.mark.asyncio
async def test_create_event_missing_subject(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="Subject is required"):
        await service.create_event(user="user1", start="2026-03-22T10:00:00Z", end="2026-03-22T11:00:00Z")


@pytest.mark.asyncio
async def test_create_event_missing_start(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="Start date/time is required"):
        await service.create_event(user="user1", subject="Meeting", end="2026-03-22T11:00:00Z")


@pytest.mark.asyncio
async def test_create_event_missing_end(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="End date/time is required"):
        await service.create_event(user="user1", subject="Meeting", start="2026-03-22T10:00:00Z")


@pytest.mark.asyncio
async def test_create_event_api_error(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_client.users.by_user_id.return_value.calendar.events.post = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.create_event(user="user1", subject="Meeting", start="2026-03-22T10:00:00Z", end="2026-03-22T11:00:00Z")


# ─── CalendarService: update_event ───

@pytest.mark.asyncio
async def test_update_event(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_event = MagicMock()
    mock_client.users.by_user_id.return_value.events.by_event_id.return_value.patch = AsyncMock(return_value=mock_event)

    result = await service.update_event(user="user1", event_id="evt1", subject="Updated Meeting")

    assert result is mock_event
    mock_client.users.by_user_id.assert_called_once_with("user1")
    mock_client.users.by_user_id.return_value.events.by_event_id.assert_called_once_with("evt1")


@pytest.mark.asyncio
async def test_update_event_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.update_event(event_id="evt1", subject="Updated")


@pytest.mark.asyncio
async def test_update_event_missing_event_id(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="Event ID is required"):
        await service.update_event(user="user1", subject="Updated")


@pytest.mark.asyncio
async def test_update_event_api_error(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_client.users.by_user_id.return_value.events.by_event_id.return_value.patch = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.update_event(user="user1", event_id="evt1", subject="Updated")


# ─── CalendarService: delete_event ───

@pytest.mark.asyncio
async def test_delete_event(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_client.users.by_user_id.return_value.events.by_event_id.return_value.delete = AsyncMock()

    result = await service.delete_event(user="user1", event_id="evt1")

    assert result is True
    mock_client.users.by_user_id.assert_called_once_with("user1")
    mock_client.users.by_user_id.return_value.events.by_event_id.assert_called_once_with("evt1")


@pytest.mark.asyncio
async def test_delete_event_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.delete_event(event_id="evt1")


@pytest.mark.asyncio
async def test_delete_event_missing_event_id(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    with pytest.raises(ValidationError, match="Event ID is required"):
        await service.delete_event(user="user1")


@pytest.mark.asyncio
async def test_delete_event_api_error(initialise_mock):
    mock_client = initialise_mock
    service = CalendarService(mock_client)

    mock_client.users.by_user_id.return_value.events.by_event_id.return_value.delete = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.delete_event(user="user1", event_id="evt1")


# ─── EmailsService: list_root_mail_folders ───

@pytest.mark.asyncio
async def test_list_root_mail_folders(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_folders = [MagicMock(display_name="Inbox"), MagicMock(display_name="Sent")]
    mock_response = MagicMock(value=mock_folders)
    mock_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=mock_response)

    result = await service.list_root_mail_folders(user="user1")

    assert result == mock_folders
    mock_client.users.by_user_id.assert_called_once_with("user1")


@pytest.mark.asyncio
async def test_list_root_mail_folders_empty(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=None)

    result = await service.list_root_mail_folders(user="user1")
    assert result is None


@pytest.mark.asyncio
async def test_list_root_mail_folders_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.list_root_mail_folders()


@pytest.mark.asyncio
async def test_list_root_mail_folders_api_error(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.list_root_mail_folders(user="user1")


# ─── EmailsService: list_child_folders ───

@pytest.mark.asyncio
async def test_list_child_folders(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_folders = [MagicMock(display_name="Subfolder1")]
    mock_response = MagicMock(value=mock_folders)
    mock_client.users.by_user_id.return_value.mail_folders.by_mail_folder_id.return_value.child_folders.get = AsyncMock(
        return_value=mock_response
    )

    result = await service.list_child_folders(user="user1", folder_id="folder1")

    assert result == mock_folders
    mock_client.users.by_user_id.assert_called_once_with("user1")
    mock_client.users.by_user_id.return_value.mail_folders.by_mail_folder_id.assert_called_once_with("folder1")


@pytest.mark.asyncio
async def test_list_child_folders_empty(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.mail_folders.by_mail_folder_id.return_value.child_folders.get = AsyncMock(
        return_value=None
    )

    result = await service.list_child_folders(user="user1", folder_id="folder1")
    assert result is None


@pytest.mark.asyncio
async def test_list_child_folders_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.list_child_folders(folder_id="folder1")


@pytest.mark.asyncio
async def test_list_child_folders_missing_folder_id(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Mail folder ID is required"):
        await service.list_child_folders(user="user1")


# ─── EmailsService: get_folder_by_name ───

@pytest.mark.asyncio
async def test_get_folder_by_name_root(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    target_folder = MagicMock(display_name="Inbox")
    other_folder = MagicMock(display_name="Sent")
    mock_response = MagicMock(value=[target_folder, other_folder])
    mock_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=mock_response)

    result = await service.get_folder_by_name(user="user1", target_folder_name="Inbox")

    assert result is target_folder


@pytest.mark.asyncio
async def test_get_folder_by_name_with_parent(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    target_folder = MagicMock(display_name="Archive")
    mock_response = MagicMock(value=[target_folder])
    mock_client.users.by_user_id.return_value.mail_folders.by_mail_folder_id.return_value.child_folders.get = AsyncMock(
        return_value=mock_response
    )

    result = await service.get_folder_by_name(user="user1", target_folder_name="Archive", parent_folder_id="parent1")

    assert result is target_folder


@pytest.mark.asyncio
async def test_get_folder_by_name_not_found(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    other_folder = MagicMock(display_name="Sent")
    mock_response = MagicMock(value=[other_folder])
    mock_client.users.by_user_id.return_value.mail_folders.get = AsyncMock(return_value=mock_response)

    result = await service.get_folder_by_name(user="user1", target_folder_name="NonExistent")

    assert result is None


@pytest.mark.asyncio
async def test_get_folder_by_name_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.get_folder_by_name(target_folder_name="Inbox")


@pytest.mark.asyncio
async def test_get_folder_by_name_missing_folder_name(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Folder name is required"):
        await service.get_folder_by_name(user="user1")


# ─── EmailsService: get_messages_in_folder ───

@pytest.mark.asyncio
async def test_get_messages_in_folder(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_messages = [MagicMock(), MagicMock()]
    mock_response = MagicMock(value=mock_messages)
    mock_client.users.by_user_id.return_value.mail_folders.by_mail_folder_id.return_value.messages.get = AsyncMock(
        return_value=mock_response
    )

    result = await service.get_messages_in_folder(user="user1", parent_folder_id="folder1")

    assert result == mock_messages
    mock_client.users.by_user_id.assert_called_once_with("user1")
    mock_client.users.by_user_id.return_value.mail_folders.by_mail_folder_id.assert_called_once_with("folder1")


@pytest.mark.asyncio
async def test_get_messages_in_folder_empty(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.mail_folders.by_mail_folder_id.return_value.messages.get = AsyncMock(
        return_value=None
    )

    result = await service.get_messages_in_folder(user="user1", parent_folder_id="folder1")
    assert result is None


@pytest.mark.asyncio
async def test_get_messages_in_folder_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.get_messages_in_folder(parent_folder_id="folder1")


@pytest.mark.asyncio
async def test_get_messages_in_folder_missing_folder_id(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Mail folder ID is required"):
        await service.get_messages_in_folder(user="user1")


# ─── EmailsService: send ───

@pytest.mark.asyncio
async def test_send(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.send_mail.post = AsyncMock()

    result = await service.send(sender="sender@test.com", to_recipients=["recipient@test.com"])

    assert result is True
    mock_client.users.by_user_id.assert_called_once_with("sender@test.com")


@pytest.mark.asyncio
async def test_send_missing_sender(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Sender is required"):
        await service.send(to_recipients=["recipient@test.com"])


@pytest.mark.asyncio
async def test_send_missing_recipients(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="At least one recipient is required"):
        await service.send(sender="sender@test.com")


@pytest.mark.asyncio
async def test_send_api_error(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.send_mail.post = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.send(sender="sender@test.com", to_recipients=["recipient@test.com"])


# ─── EmailsService: reply ───

@pytest.mark.asyncio
async def test_reply(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.messages.by_message_id.return_value.reply.post = AsyncMock()

    result = await service.reply(sender="sender@test.com", message_id="msg1", comment="Thanks")

    assert result is True
    mock_client.users.by_user_id.assert_called_once_with("sender@test.com")
    mock_client.users.by_user_id.return_value.messages.by_message_id.assert_called_once_with("msg1")


@pytest.mark.asyncio
async def test_reply_missing_sender(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Sender is required"):
        await service.reply(message_id="msg1")


@pytest.mark.asyncio
async def test_reply_missing_message_id(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Message Id is required"):
        await service.reply(sender="sender@test.com")


# ─── EmailsService: reply_all ───

@pytest.mark.asyncio
async def test_reply_all(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.messages.by_message_id.return_value.reply_all.post = AsyncMock()

    result = await service.reply_all(sender="sender@test.com", message_id="msg1", comment="Noted")

    assert result is True
    mock_client.users.by_user_id.assert_called_once_with("sender@test.com")
    mock_client.users.by_user_id.return_value.messages.by_message_id.assert_called_once_with("msg1")


@pytest.mark.asyncio
async def test_reply_all_missing_sender(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Sender is required"):
        await service.reply_all(message_id="msg1")


@pytest.mark.asyncio
async def test_reply_all_missing_message_id(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Message Id is required"):
        await service.reply_all(sender="sender@test.com")


# ─── EmailsService: forward ───

@pytest.mark.asyncio
async def test_forward(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.messages.by_message_id.return_value.forward.post = AsyncMock()

    result = await service.forward(
        sender="sender@test.com", message_id="msg1", to_recipients=["forward@test.com"]
    )

    assert result is True
    mock_client.users.by_user_id.assert_called_once_with("sender@test.com")
    mock_client.users.by_user_id.return_value.messages.by_message_id.assert_called_once_with("msg1")


@pytest.mark.asyncio
async def test_forward_missing_sender(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Sender is required"):
        await service.forward(message_id="msg1", to_recipients=["forward@test.com"])


@pytest.mark.asyncio
async def test_forward_missing_message_id(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Message Id is required"):
        await service.forward(sender="sender@test.com", to_recipients=["forward@test.com"])


@pytest.mark.asyncio
async def test_forward_missing_recipients(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="At least one recipient is required"):
        await service.forward(sender="sender@test.com", message_id="msg1")


# ─── EmailsService: delete ───

@pytest.mark.asyncio
async def test_delete_message(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.messages.by_message_id.return_value.delete = AsyncMock()

    result = await service.delete(user="user1", message_id="msg1")

    assert result is True
    mock_client.users.by_user_id.assert_called_once_with("user1")
    mock_client.users.by_user_id.return_value.messages.by_message_id.assert_called_once_with("msg1")


@pytest.mark.asyncio
async def test_delete_message_missing_user(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="User is required"):
        await service.delete(message_id="msg1")


@pytest.mark.asyncio
async def test_delete_message_missing_message_id(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    with pytest.raises(ValidationError, match="Message Id is required"):
        await service.delete(user="user1")


@pytest.mark.asyncio
async def test_delete_message_api_error(initialise_mock):
    mock_client = initialise_mock
    service = EmailsService(mock_client)

    mock_client.users.by_user_id.return_value.messages.by_message_id.return_value.delete = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.delete(user="user1", message_id="msg1")
