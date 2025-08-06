from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.item.copy.copy_post_request_body import CopyPostRequestBody
from msgraph.generated.models.item_reference import ItemReference
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder

class SharepointService():
    def __init__(self, graph_client: GraphServiceClient):

        self.graph_client = graph_client

        if not graph_client:
            raise ValueError("msgraph client must be supplied")
        

        
    async def create_folder(self, location_id, folder_name=None):
        """Creates a folder in a defined location."""

        confirmed_folder_name = folder_name if folder_name else "New Folder"

        request_body = DriveItem(
            name = confirmed_folder_name,
            folder = Folder(
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        # where to create the new folder
        await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(location_id).children.post(request_body)

