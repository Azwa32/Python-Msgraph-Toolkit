from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from .chat import ChatService
from ..exceptions import ValidationError


class TeamsService():
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        
        # Initialize sub-services
        self.chat = ChatService(self._msgraph_client)