from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from .sites import SitesService
from .drives import DriveService
from .files import FileService
import re


class SharepointService():
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
        # Initialize sub-services
        self.sites = SitesService(self._msgraph_client)
        self.files = FileService(self._msgraph_client)
        self.drives = DriveService(self._msgraph_client)



