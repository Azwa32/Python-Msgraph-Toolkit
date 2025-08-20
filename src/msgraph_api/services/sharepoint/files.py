from msgraph import GraphServiceClient
from msgraph.generated.drives.item.items.items_request_builder import ItemsRequestBuilder 
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration

class FileService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
        # for exceeding the return limit of the graph api without using pagenation
    def _exceed_drive_query(self):
        drive_query_size = 1000     # this would be the most amount of customers FocusAv expects to have
        query_params = ItemsRequestBuilder .ItemsRequestBuilderGetQueryParameters(
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
        try:
            return await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id)\
                .children.get(request_configuration = self._exceed_drive_query())
        except Exception as e:
            print(f"Exception list_folders: {e}") 

    


    async def get_folder_by_name(self, drive_id : str=None, parent_folder_id : str=None, child_folder_name : str=None):
        query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(
            filter=f"name eq '{child_folder_name}'"
            #top=100,
        )
        request_config = RequestConfiguration(query_parameters=query_params)                
        try:
            response = await self._msgraph_client.drives.by_drive_id(drive_id)\
                .items.by_drive_item_id(parent_folder_id).children.get(request_config) 
            if response:           
                return response.value[0]
            return None            
        except Exception as e:
            print(f"Exception get_folder_by_name: {e}")



    async def get_item_by_path(self, drive_id: str, item_path: str):
        """Get folder or file by path"""
        try:           
            # Direct path access
            item = await self._msgraph_client.drives.by_drive_id(drive_id).root \
            .with_url(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{item_path}") \
            .get()
            
            return item
            
        except Exception as e:
            print(f"Error getting item at path '{item_path}': {e}")
            return None
