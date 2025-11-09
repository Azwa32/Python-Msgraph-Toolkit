from msgraph import GraphServiceClient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from .emails import EmailsService
from .calendar import CalendarService
import re


class OutlookService():
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
        # Initialize sub-services
        self.emails = EmailsService(self._msgraph_client)
        self.calendar = CalendarService(self._msgraph_client)
