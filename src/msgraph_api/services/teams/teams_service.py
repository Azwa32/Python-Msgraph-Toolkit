from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from .channel import ChannelService
from .chat import ChatService
from .meeting import MeetingService
import re


class SharepointService():
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
        # Initialize sub-services
        self.sites = ChannelService(self._msgraph_client)
        self.files = ChatService(self._msgraph_client)
        self.drives = MeetingService(self._msgraph_client)