from msgraph import GraphServiceClient


class DriveService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied") 

    async def get_drive_root_folder(self, **kwargs):
        """
        Retrieve the root folder of a specific drive.
        #### Args:
            drive_id (str): The unique identifier for the SharePoint drive
        #### Returns:
            DriveItem: The root folder of the specified drive, or None if not found
        #### Usage example:
            >>> root_folder = await drive_service.get_drive_root_folder(drive_id="my_drive_id")
            >>> if root_folder:
            ...     print(f"Root folder name: {root_folder.name}")
            ...     print(f"Root folder ID: {root_folder.id}")
            ...     print(f"Root folder URL: {root_folder.web_url}")
        """
        drive_id = kwargs.get("drive_id", "")
        
        if not drive_id:
            print("No Drive ID entered, please enter Drive ID")
            return
        try:
            return await self._msgraph_client.drives.by_drive_id(drive_id).root.get()
        except Exception as e:
            print(f"Error get_all_folders: {e}")


