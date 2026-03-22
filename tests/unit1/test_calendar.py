import pytest
from unittest.mock import AsyncMock, MagicMock

from src.python_msgraph_toolkit.services.outlook.calendar import CalendarService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError


class TestCalendarServiceInit:
    def test_init_with_valid_client(self, mock_graph_client):
        service = CalendarService(mock_graph_client)
        assert service._msgraph_client is mock_graph_client

    def test_init_with_none_client_raises(self):
        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            CalendarService(None)


class TestGetEvents:
    @pytest.fixture
    def calendar_service(self, mock_graph_client):
        return CalendarService(mock_graph_client)

    async def test_missing_user_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="User is required"):
            await calendar_service.get_events()

    async def test_get_all_events_no_date_filter(self, calendar_service, mock_graph_client):
        events = [MagicMock(subject="Meeting"), MagicMock(subject="Lunch")]
        mock_response = MagicMock(value=events)
        mock_graph_client.users.by_user_id.return_value \
            .calendar.events.get = AsyncMock(return_value=mock_response)

        result = await calendar_service.get_events(user="user@test.com")
        assert result == events

    async def test_get_events_with_date_range(self, calendar_service, mock_graph_client):
        events = [MagicMock(subject="Event")]
        mock_response = MagicMock(value=events)
        mock_graph_client.users.by_user_id.return_value \
            .calendar.events.get = AsyncMock(return_value=mock_response)

        result = await calendar_service.get_events(
            user="user@test.com",
            start_date="2026-01-01T00:00:00Z",
            end_date="2026-01-31T23:59:59Z",
        )
        assert result == events

    async def test_no_events_returns_none(self, calendar_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.users.by_user_id.return_value \
            .calendar.events.get = AsyncMock(return_value=mock_response)

        result = await calendar_service.get_events(user="user@test.com")
        assert result is None

    async def test_api_error_raises(self, calendar_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .calendar.events.get = AsyncMock(side_effect=Exception("calendar error"))

        with pytest.raises(GraphAPIError):
            await calendar_service.get_events(user="user@test.com")


class TestCreateEvent:
    @pytest.fixture
    def calendar_service(self, mock_graph_client):
        return CalendarService(mock_graph_client)

    async def test_missing_user_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="User is required"):
            await calendar_service.create_event(subject="Test", start="2026-01-01", end="2026-01-02")

    async def test_missing_subject_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="Subject is required"):
            await calendar_service.create_event(user="user@test.com", start="2026-01-01", end="2026-01-02")

    async def test_missing_start_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="Start date/time is required"):
            await calendar_service.create_event(user="user@test.com", subject="Test", end="2026-01-02")

    async def test_missing_end_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="End date/time is required"):
            await calendar_service.create_event(user="user@test.com", subject="Test", start="2026-01-01")

    async def test_successful_create(self, calendar_service, mock_graph_client):
        mock_event = MagicMock(subject="Team Meeting")
        mock_graph_client.users.by_user_id.return_value \
            .calendar.events.post = AsyncMock(return_value=mock_event)

        result = await calendar_service.create_event(
            user="user@test.com",
            subject="Team Meeting",
            start="2026-03-22T10:00:00",
            end="2026-03-22T11:00:00",
            location="Room A",
            body="Agenda items",
            attendees=["bob@test.com"],
            pre_event_reminder=15,
        )
        assert result is mock_event
        mock_graph_client.users.by_user_id.return_value \
            .calendar.events.post.assert_awaited_once()

    async def test_create_with_minimal_params(self, calendar_service, mock_graph_client):
        mock_event = MagicMock()
        mock_graph_client.users.by_user_id.return_value \
            .calendar.events.post = AsyncMock(return_value=mock_event)

        result = await calendar_service.create_event(
            user="user@test.com",
            subject="Quick Chat",
            start="2026-03-22T10:00:00",
            end="2026-03-22T10:30:00",
        )
        assert result is mock_event


class TestUpdateEvent:
    @pytest.fixture
    def calendar_service(self, mock_graph_client):
        return CalendarService(mock_graph_client)

    async def test_missing_user_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="User is required"):
            await calendar_service.update_event(event_id="evt1")

    async def test_missing_event_id_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="Event ID is required"):
            await calendar_service.update_event(user="user@test.com")

    async def test_successful_update(self, calendar_service, mock_graph_client):
        mock_updated = MagicMock(subject="Updated Meeting")
        mock_graph_client.users.by_user_id.return_value \
            .events.by_event_id.return_value \
            .patch = AsyncMock(return_value=mock_updated)

        result = await calendar_service.update_event(
            user="user@test.com",
            event_id="evt1",
            subject="Updated Meeting",
            location="Room B",
        )
        assert result is mock_updated

    async def test_update_api_error_raises(self, calendar_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .events.by_event_id.return_value \
            .patch = AsyncMock(side_effect=Exception("update failed"))

        with pytest.raises(GraphAPIError):
            await calendar_service.update_event(user="user@test.com", event_id="evt1", subject="New")


class TestDeleteEvent:
    @pytest.fixture
    def calendar_service(self, mock_graph_client):
        return CalendarService(mock_graph_client)

    async def test_missing_user_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="User is required"):
            await calendar_service.delete_event(event_id="evt1")

    async def test_missing_event_id_raises(self, calendar_service):
        with pytest.raises(ValidationError, match="Event ID is required"):
            await calendar_service.delete_event(user="user@test.com")

    async def test_successful_delete(self, calendar_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .events.by_event_id.return_value \
            .delete = AsyncMock()

        result = await calendar_service.delete_event(user="user@test.com", event_id="evt1")
        assert result is True

    async def test_delete_api_error_raises(self, calendar_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value \
            .events.by_event_id.return_value \
            .delete = AsyncMock(side_effect=Exception("delete failed"))

        with pytest.raises(GraphAPIError):
            await calendar_service.delete_event(user="user@test.com", event_id="evt1")
