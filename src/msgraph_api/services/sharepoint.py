from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
import re

class SharepointService():
    def __init__(self, graph_client: GraphServiceClient):
        self.graph_client = graph_client
        if not graph_client:
            raise ValueError("msgraph client must be supplied")
        
    def _convert_path_to_id(self, loc):
        # path to id conversion logic
        return loc
        
    def _location_type_convert(self, loc):
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
            return self._convert_path_to_id(loc)
        
        raise ValueError(f"Location does not match any pattern: {loc}")


    async def create_folder(self, drive_id : str, location_id : str, folder_name :str=None):
        """
        Create a folder under a parent location within a specific drive.

        Args:
            drive_id: The target drive identifier (e.g., a GUID/Graph drive ID) or site name. Accepts:
                - a drive ID
                - a site name
            location_id: The parent folder location within the drive. Accepts:
                - a folder/item ID (e.g., '01...') or the literal 'root'
                - a folder path (e.g., '/Documents/Projects'), which will be resolved to an ID
            folder_name: Name of the new folder. Defaults to "New Folder" if not provided.

        Returns:
            DriveItem: The created folder item returned by Microsoft Graph.

        Raises:
            ValueError: If drive_id or location_id cannot be interpreted as a valid ID or path.
        """

        confirmed_folder_name = folder_name if folder_name else "New Folder"

        request_body = DriveItem(
            name = confirmed_folder_name,
            folder = Folder(
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        drive_location = self._location_type_convert(drive_id)
        parent_location = self._location_type_convert(location_id)
        try:
            return await self.graph_client.drives.by_drive_id(drive_location).items.by_drive_item_id(parent_location).children.post(request_body)
        except Exception as e:
            print(f"failed to create folder: {e}")

    #client.sharepoint.lists.get_all()
    async def get_all_sites(self):
        response = await self.graph_client.sites.get_all_sites.get()
        children = response.value                                 # pulls values from the graph api response
        for child in children:    
            print(child.name)
        



