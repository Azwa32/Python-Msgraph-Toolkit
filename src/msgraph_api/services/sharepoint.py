from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.copy.copy_post_request_body import CopyPostRequestBody
from msgraph.generated.models.item_reference import ItemReference
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from ..utils.pattern_id import is_id_type
import re

class SharepointService():
    def __init__(self, graph_client: GraphServiceClient):
        self.graph_client = graph_client
        if not graph_client:
            raise ValueError("msgraph client must be supplied")
        
    def convert_path_to_id(self, loc):
        # path to id conversion logic
        return loc
        
    def location_type_convert(self, loc):
        """
        Checks input and returns a converted (or unconverted) location id
        """

        # check and process as guid
        guid_pattern = re.compile(
            r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        )
        if guid_pattern.match(loc):
            return loc

        # check and process as folder path
        if "/" in loc:
            self.convert_path_to_loc(loc)



        
        
    async def create_folder(self, drive_id, location_id, folder_name=None):
        """Creates a folder in a pre-defined Sharepoint location."""

        confirmed_folder_name = folder_name if folder_name else "New Folder"

        request_body = DriveItem(
            name = confirmed_folder_name,
            folder = Folder(
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        drive_location = "function to return drive loc"
        parent_location = "function to return parent loc"
        # where to create the new folder
        await self.graph_client.drives.by_drive_id(drive_location).items.by_drive_item_id(parent_location).children.post(request_body)


