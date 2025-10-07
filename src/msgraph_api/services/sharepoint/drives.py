from msgraph import GraphServiceClient


class DriveService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied") 

    async def get_drive_root_folder(self, **kwargs):
        drive_id = kwargs.get("drive_id", "")
        
        if not drive_id:
            print("No Drive ID entered, please enter Drive ID")
            return
        try:
            return await self._msgraph_client.drives.by_drive_id(drive_id).root.get()
        except Exception as e:
            print(f"Error get_all_folders: {e}")


