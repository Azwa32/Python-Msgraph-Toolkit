from typing import List, Optional
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
from msgraph.generated.models.event import Event
import logging
from ..exceptions import ValidationError, graph_exception_handler

class CalendarService:
    """Service for managing Email through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient) -> None:
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")       

    async def get_events(
                self,
                *,
                user : str,
                start_date : Optional[str] = None,
                end_date : Optional[str] = None,
        ):

        if not user or not user.strip():
            raise ValidationError("User is required")

        try:   
            events = None
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
                    
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return None
        
    async def create_event(
                self,
                *,
                user : str,
                subject : str,
                start : str,
                end : str,
                location : Optional[str] = None,
                body : Optional[str] = None,
                attendees : Optional[List[str]] = None,
                pre_event_reminder : Optional[int] = None,
        ):

        if not user or not user.strip():
            raise ValidationError("User is required")
        if not subject or not subject.strip():
            raise ValidationError("Subject is required")
        if not start or not start.strip():
            raise ValidationError("Start date/time is required")
        if not end or not end.strip():
            raise ValidationError("End date/time is required")
        if not body:
            body = ""
        if attendees is None:
            attendees = []

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
            event = await self._msgraph_client.users.by_user_id(user).calendar.events.post(request_body)
            return event
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return None
        

    async def update_event(
                self,
                *,
                user : str,
                event_id : str,
                subject : Optional[str] = None,
                start : Optional[str] = None,
                end : Optional[str] = None,
                location : Optional[str] = None,
                body : Optional[str] = None,
                attendees : Optional[List[str]] = None,
                pre_event_reminder : Optional[int] = None,
        ):

        if not user or not user.strip():
            raise ValidationError("User is required")
        if not event_id or not event_id.strip():
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
            graph_exception_handler(e, "Outlook")
            return None
        

    async def delete_event(
                self,
                *,
                user : str,
                event_id : str,
        ):

        if not user or not user.strip():
            raise ValidationError("User is required")
        if not event_id or not event_id.strip():
            raise ValidationError("Event ID is required")
        try:
            await self._msgraph_client.users.by_user_id(user).events.by_event_id(event_id).delete()
            return True
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return False
        
        
