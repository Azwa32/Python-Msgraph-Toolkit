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
            start_date (str, optional): The start date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            end_date (str, optional): The end date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            
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
            body (str, optional): The body content of the event.
            start (str): The start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            end (str): The end date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            location (str, optional): The location of the event.
            attendees (List[str], optional): A list of attendee email addresses.
            pre_event_reminder (int, optional): Reminder time in minutes before the event.

        Returns:
            Event object if successful, None otherwise.
        """

        user = kwargs.get("user") # required
        subject = kwargs.get("subject") # required
        start = kwargs.get("start") # required
        end = kwargs.get("end") # required
        location = kwargs.get("location")
        body = kwargs.get("body")
        attendees = kwargs.get("attendees", [])
        pre_event_reminder = kwargs.get("pre_event_reminder")

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
            reminder_minutes_before_start = pre_event_reminder if pre_event_reminder else None,
        )
        try:
            event = await self._msgraph_client.users.by_user_id(user).calendars.by_calendar_id('calendar-id').events.post(request_body)
            return event
        except Exception as e:
            self._exception_helper(e)
            return None
        

    async def update_event(self, **kwargs):
        """Update an existing calendar event.

        Args:
            user (str): The user ID or email address.
            event_id (str): The ID of the event to update.
            subject (str, optional): New subject for the event.
            body (str, optional): New body content for the event.
            start (str, optional): New start date and time in ISO 8601 format.
            end (str, optional): New end date and time in ISO 8601 format.
            location (str, optional): New location for the event.
            attendees (List[str], optional): New list of attendee email addresses.
            pre_event_reminder (int, optional): New reminder time in minutes before the event.
            
        Returns:
            Updated event object if successful, None otherwise.
        """
        user = kwargs.get("user") # required
        event_id = kwargs.get("event_id") # required
        subject = kwargs.get("subject")
        start = kwargs.get("start")
        end = kwargs.get("end")
        location = kwargs.get("location")
        body = kwargs.get("body")
        attendees = kwargs.get("attendees", [])
        pre_event_reminder = kwargs.get("pre_event_reminder")

        if not user:
            raise ValidationError("User is required")
        if not event_id:
            raise ValidationError("Event ID is required")
        
        request_body = Event()
        if subject is not None:
            request_body.subject = subject
        
        if start is not None:
            request_body.start = DateTimeTimeZone(
                date_time = start,
                time_zone = "Pacific Standard Time",
            )

        if end is not None:
            request_body.end = DateTimeTimeZone(
                date_time = end,
                time_zone = "Pacific Standard Time",
            )

        if location is not None:
            request_body.location = Location(
                display_name = location,
            )
        
        if body is not None:
            request_body.body = ItemBody(
                content_type = BodyType.Html,
                content = body,
            )

        if attendees is not None:
            attendees_list = []
            for attendee in attendees:
                attendees_list.append(Attendee(email_address = EmailAddress(
                                                address = attendee,                      
                )))
            request_body.attendees = attendees_list

        if pre_event_reminder is not None:
            request_body.reminder_minutes_before_start = pre_event_reminder

        try:
            event = await self._msgraph_client.users.by_user_id(user).events.by_event_id(event_id).patch(request_body)
            return event
        except Exception as e:
            self._exception_helper(e)
            return None
        

    async def delete_event(self, **kwargs):
        """Delete a calendar event.

        Args:
            user (str): The user ID or email address.
            event_id (str): The ID of the event to delete.
            
        Returns:
            bool: True if deletion successful, False otherwise.
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
        
        
