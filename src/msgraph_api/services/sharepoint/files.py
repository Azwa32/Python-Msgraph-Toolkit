from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder   
from kiota_abstractions.base_request_configuration import RequestConfiguration

class FileService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
        # for exceeding the return limit of the graph api without using pagenation
    def _exceed_drive_query(self):
        drive_query_size = 1000     # this would be the most amount of customers FocusAv expects to have
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
		    top = drive_query_size          
            )
        request_configuration = RequestConfiguration(
            query_parameters = query_params,
            )
        return request_configuration
        
    async def list_folders(self, drive_id : str=None, parent_folder_id : str=None):
        if not drive_id:
            print("No Drive ID entered, please enter Drive ID")
            return
        if not parent_folder_id:
            print("No parent folder ID entered, please enter parent folder ID")
            return
        return await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id).children.get(request_configuration = self._exceed_drive_query())
    
    async def get_folder_id_by_name(self, drive_id : str=None, parent_folder_id : str=None, child_folder_name : str=None):
        response = await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id).children.get(request_configuration = self._exceed_drive_query())
        values = response.value                                 # pulls values from the graph api response
        for child in values:    
            if child.name == child_folder_name:                 # finds id of a folder that matches the child folder name  
                folder_id = child.id
                return folder_id
        return response.value