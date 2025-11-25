from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from .channels import ChannelsService
from .chat import ChatService
from .meetings import MeetingsService
import re


class SharepointService():
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
        # Initialize sub-services
        self.channels = ChannelsService(self._msgraph_client)
        self.chat = ChatService(self._msgraph_client)
        self.meetings = MeetingsService(self._msgraph_client)