from msgraph.graph_service_client import GraphServiceClient
from ..exceptions import ValidationError, graph_exception_handler


class DriveService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied") 

    async def get_drive_root_folder(
                self,
                *,
                drive_id : str,
        ):

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required")
        try:
            return await self._msgraph_client.drives.by_drive_id(drive_id).root.get()
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return None # This line will never be reached due to exception being raised, but is here to satisfy return type


