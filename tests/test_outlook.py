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

@pytest.mark.asyncio
async def test_send(initialize_client):
    subject="Test Email",
    body="This is a test email",
    sender=str(os.getenv("TEST_OUTLOOK_USER_EMAIL")),
    to_recipients=[str(os.getenv("TEST_OUTLOOK_TO_RECIPIENT"))],
    cc_recipients=[str(os.getenv("TEST_OUTLOOK_TO_RECIPIENT"))],
    bcc_recipients=[str(os.getenv("TEST_OUTLOOK_BCC_RECIPIENT"))],
    reply_to=(str(os.getenv("TEST_OUTLOOK_REPLY_TO_RECIPIENT"))),
    priority="Normal",
    client = initialize_client
    result = await client.outlook.emails.send(
        subject=subject,
        body=body,
        sender=sender,
        to_recipients=to_recipients,
        cc_recipients=cc_recipients,
        bcc_recipients=bcc_recipients,
        reply_to=reply_to,
        priority=priority
    )
    assert result is True

@pytest.mark.asyncio
async def test_reply(initialize_client):
    sender = str(os.getenv("TEST_USER_EMAIL"))
    message_id = str(os.getenv("TEST_OUTLOOK_MESSAGE_ID"))
    comment = "This is a test reply"
    reply_to_recipients = [str(os.getenv("TEST_OUTLOOK_REPLY_TO_RECIPIENT"))]
    client = initialize_client
    result = await client.outlook.emails.reply(
        sender=sender,
        message_id=message_id,
        comment=comment,
        reply_to_recipients=reply_to_recipients
    )
    assert result is True

@pytest.mark.asyncio
async def test_reply_all(initialize_client):
    sender = str(os.getenv("TEST_USER_EMAIL"))
    message_id = str(os.getenv("TEST_OUTLOOK_MESSAGE_ID"))
    comment = "This is a test reply all"
    reply_to_recipients = [str(os.getenv("TEST_OUTLOOK_REPLY_TO_RECIPIENT"))]
    client = initialize_client
    result = await client.outlook.emails.reply_all(
        sender=sender,
        message_id=message_id,
        comment=comment,
        reply_to_recipients=reply_to_recipients
    )
    assert result is True

@pytest.mark.asyncio
async def test_forward(initialize_client):
    sender = str(os.getenv("TEST_USER_EMAIL"))
    message_id = str(os.getenv("TEST_OUTLOOK_MESSAGE_ID"))
    comment = "This is a test forward"
    to_recipients = [str(os.getenv("TEST_OUTLOOK_TO_RECIPIENT"))]
    client = initialize_client
    result = await client.outlook.emails.forward(
        sender=sender,
        message_id=message_id,
        comment=comment,
        to_recipients=to_recipients
    )
    assert result is True

@pytest.mark.asyncio
async def test_delete(initialize_client):
    user_email = str(os.getenv("TEST_OUTLOOK_USER_EMAIL"))
    message_id = str(os.getenv("TEST_OUTLOOK_MESSAGE_ID_TO_DELETE"))
    client = initialize_client
    result = await client.outlook.emails.delete(user=user_email, message_id=message_id)
    assert result is True

@pytest.mark.asyncio
async def test_get_events(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    client = initialize_client
    events = await client.outlook.calendar.get_events(user=user_id)
    assert events is not None
    assert isinstance(events, list)

@pytest.mark.asyncio
async def test_get_events_by_date_range(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    start_datetime = str(os.getenv("TEST_EVENT_START_DATETIME"))
    end_datetime = str(os.getenv("TEST_EVENT_END_DATETIME"))
    client = initialize_client
    events = await client.outlook.calendar.get_events_by_date_range(
        user=user_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )
    assert events is not None
    assert isinstance(events, list)

@pytest.mark.asyncio
async def test_create_event(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    subject = "Test Event"
    body = "This is a test event"
    start_datetime = str(os.getenv("TEST_EVENT_START_DATETIME"))
    end_datetime = str(os.getenv("TEST_EVENT_END_DATETIME"))
    attendees = [str(os.getenv("TEST_EVENT_ATTENDEE_EMAIL"))]
    client = initialize_client
    event = await client.outlook.calendar.create_event(
        user=user_id,
        subject=subject,
        body=body,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        attendees=attendees
    )
    assert event is not None
    assert event.subject == subject
    assert event.body.content == body
    assert event.start.date_time == start_datetime
    assert event.end.date_time == end_datetime
    assert any(attendee.email_address.address == attendees[0] for attendee in event.attendees)

@pytest.mark.asyncio
async def test_update_event(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    event_id = str(os.getenv("TEST_EVENT_ID"))
    new_subject = "Updated Test Event"
    new_start = str(os.getenv("TEST_EVENT_NEW_START_DATETIME"))
    new_end = str(os.getenv("TEST_EVENT_NEW_END_DATETIME"))
    new_location = str(os.getenv("TEST_EVENT_NEW_LOCATION"))
    new_body = "This is an updated test event"
    new_attendees = [str(os.getenv("TEST_EVENT_NEW_ATTENDEE_EMAIL"))]
    new_pre_event_reminder = str(os.getenv("TEST_EVENT_NEW_PRE_EVENT_REMINDER"))
    client = initialize_client
    updated_event = await client.outlook.calendar.update_event(
        user=user_id,
        event_id=event_id,
        subject=new_subject,
        start_datetime=new_start,
        end_datetime=new_end,
        location=new_location,
        body=new_body,
        attendees=new_attendees,
        pre_event_reminder=new_pre_event_reminder
    )
    assert updated_event is not None
    assert updated_event.subject == new_subject
    assert updated_event.start.date_time == new_start
    assert updated_event.end.date_time == new_end
    assert updated_event.location.display_name == new_location
    assert updated_event.body.content == new_body
    assert any(attendee.email_address.address == new_attendees[0] for attendee in updated_event.attendees)
    assert updated_event.reminder_minutes_before_start == int(new_pre_event_reminder)

@pytest.mark.asyncio
async def test_delete_event(initialize_client):
    user_id = str(os.getenv("TEST_USER_ID"))
    event_id = str(os.getenv("TEST_EVENT_ID_TO_DELETE"))
    client = initialize_client
    result = await client.outlook.calendar.delete_event(user=user_id, event_id=event_id)
    assert result is True
