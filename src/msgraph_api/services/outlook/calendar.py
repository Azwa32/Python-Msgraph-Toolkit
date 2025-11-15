from msgraph.generated.models.calendar import Calendar
from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.users.item.calendar.events.events_request_builder import EventsRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.event import Event
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.location import Location
from msgraph.generated.models.attendee import Attendee
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.attendee_type import AttendeeType
from msgraph.generated.models.event import Event
from msgraph.generated.models.response_status import ResponseStatus
from msgraph.generated.models.response_type import ResponseType
from msgraph.generated.models.online_meeting_provider_type import OnlineMeetingProviderType
from functools import wraps
import logging
from typing import List, Optional

from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError,
)

class CalendarService:
    """Service for managing Email through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient) -> None:
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        
    def _exception_helper(self, exception : Exception):
        self.logger.error(f"SharePoint operation failed: {exception}", exc_info=True)
        error_str = str(exception).lower()
        # Handle specific Azure AD errors
        if '900023' in error_str or 'aadsts90002' in error_str:
            raise AuthenticationError("Invalid Tenant ID. Verify MSGRAPH_TENANT_ID and try again") from exception
        
        elif '700016' in error_str or 'aadsts700016' in error_str:
            raise AuthenticationError("Invalid Client ID. Verify MSGRAPH_CLIENT_ID and try again") from exception
        
        elif '7000215' in error_str or 'aadsts7000215' in error_str:
            raise AuthenticationError("Invalid Client Secret. Verify MSGRAPH_API_KEY and try again") from exception
        
        elif 'not found' in error_str or '404' in error_str:
            raise SharePointError("SharePoint resource not found") from exception
        
        elif 'forbidden' in error_str or '403' in error_str:
            raise SharePointError("Access denied to SharePoint resource") from exception
        
        elif 'rate limit' in error_str or '429' in error_str:
            raise RateLimitError("API rate limit exceeded") from exception
        
        else:
            raise SharePointError(f"SharePoint operation failed: {exception}") from exception
        

    async def get_events(self, **kwargs):
        """Get calendar events for a user within a specified date range.

        Args:
            user (str): The user ID or email address.
            start_date (str): Optional, The start date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            end_date (str): Optional, The end date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).

        Returns:
            Optional[List[dict]]: A list of calendar events or None if an error occurs.
        """
        user = kwargs.get("user") # required
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        if not user:
            raise ValidationError("User is required")
        
        if not start_date or not end_date:
            events = await self._msgraph_client.users.by_user_id(user).calendar.events.get()
            
        else:        
            query_params = EventsRequestBuilder.EventsRequestBuilderGetQueryParameters(
                filter = f"start/dateTime ge '{start_date}' and end/dateTime le '{end_date}'",
                orderby=["start/dateTime ASC"]
            )

            request_configuration = RequestConfiguration(
            query_parameters = query_params,
            )
            events = await self._msgraph_client.users.by_user_id(user).calendar.events.get(request_configuration = request_configuration)
        
        if events and events.value:
            return events.value
        
    async def create_event(self, **kwargs):
        """Create a new calendar event for a user.

        Args:
            user (str): The user ID or email address.
            subject (str): The subject of the event.
            body (str): The body content of the event.
            start (str): The start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            end (str): The end date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            attendees (List[str], optional): A list of attendee email addresses."""

        user = kwargs.get("user") # required
        subject = kwargs.get("subject") # required
        start = kwargs.get("start") # required
        end = kwargs.get("end") # required
        location = kwargs.get("location")
        body = kwargs.get("body")
        attendees = kwargs.get("attendees", [])

        if not user:
            raise ValidationError("User is required")
        if not subject:
            raise ValidationError("Subject is required")
        if not start:
            raise ValidationError("Start date/time is required")
        if not end:
            raise ValidationError("End date/time is required")
        if not body:
            body = ""

        attendees_list = []
        if attendees:
            for attendee in attendees:
                attendees_list.append(Attendee(email_address = EmailAddress(
                                                address = attendee,                      
                )))

        request_body = Event(
            subject = subject,
            body = ItemBody(
                content_type = BodyType.Html,
                content = body,
            ),
            start = DateTimeTimeZone(
                date_time = start,
                time_zone = "Pacific Standard Time",
            ),
            end = DateTimeTimeZone(
                date_time = end,
                time_zone = "Pacific Standard Time",
            ),
            location = Location(
                display_name = location,
            ),
            attendees = attendees_list if attendees_list else None,
        )
        try:
            created_event = await self._msgraph_client.users.by_user_id(user).calendars.by_calendar_id('calendar-id').events.post(request_body)
            return created_event
        except Exception as e:
            self._exception_helper(e)
            return None
        

    async def update_event(self, **kwargs):
        """Update a calendar event.

        Args:
            user (str): The user ID or email address.
            event_id (str): The ID of the event to update.            
        """
        user = kwargs.get("user") # required
        event_id = kwargs.get("event_id") # required
        subject = kwargs.get("subject") # required
        start = kwargs.get("start") # required
        end = kwargs.get("end") # required
        location = kwargs.get("location")
        body = kwargs.get("body")
        attendees = kwargs.get("attendees", [])

        if not user:
            raise ValidationError("User is required")
        if not event_id:
            raise ValidationError("Event ID is required")
        
        request_body = Event(
            original_start_time_zone = "originalStartTimeZone-value",
            original_end_time_zone = "originalEndTimeZone-value",
            response_status = ResponseStatus(
                response = ResponseType.None,
                time = "datetime-value",
            ),
            recurrence = None,
            reminder_minutes_before_start = 99,
            is_online_meeting = True,
            online_meeting_provider = OnlineMeetingProviderType.TeamsForBusiness,
            is_reminder_on = True,
            hide_attendees = False,
            categories = [
                "Red category",
            ],
        )

        try:
            await self._msgraph_client.users.by_user_id(event_id).events.by_event_id('event-id').patch(updates)
            return True
        except Exception as e:
            self._exception_helper(e)
            return False
        

    async def delete_event(self, **kwargs):
        """Delete a calendar event.

        Args:
            user (str): The user ID or email address.
            event_id (str): The ID of the event to delete.
        """
        user = kwargs.get("user") # required
        event_id = kwargs.get("event_id") # required

        if not user:
            raise ValidationError("User is required")
        if not event_id:
            raise ValidationError("Event ID is required")
        try:
            await self._msgraph_client.users.by_user_id(user).events.by_event_id(event_id).delete()
            return True
        except Exception as e:
            self._exception_helper(e)
            return False
        
        
