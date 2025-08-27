from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from msgraph.generated.models.item_reference import ItemReference
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.drives.item.items.items_request_builder import ItemsRequestBuilder 
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
from msgraph.generated.drives.item.search_with_q.search_with_q_request_builder import SearchWithQRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from typing import Optional, List, Dict, Any
import logging

# Import your existing exceptions
from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError
)

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
    def _exceed_drive_query(self):
        """For exceeding the return limit of the graph api without using pagenation"""
        drive_query_size = 1000
        query_params = ItemsRequestBuilder .ItemsRequestBuilderGetQueryParameters(
		    top = drive_query_size          
            )
        request_configuration = RequestConfiguration(
            query_parameters = query_params,
            )
        return request_configuration
        

    async def list_folder_contents(self, drive_id : str=None, parent_folder_id : str=None):
        """Returns a list of contents objects in parent_folder"""
        if not drive_id:
            print("No Drive ID entered, please enter Drive ID")
            return
        if not parent_folder_id:
            print("No parent folder ID entered, please enter parent folder ID")
            return
        try:
            response =  await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id)\
                .children.get(request_configuration = self._exceed_drive_query())
            return response.value
        except Exception as e:
            print(f"Exception list_folders: {e}")     


    async def get_item_by_name(self, drive_id : str=None, parent_folder_id : str=None, item_name : str=None):
        """Returns the object with matching item_name in parent_folder"""
        query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(
            filter=f"name eq '{item_name}'"
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
        """Returns the object with matching item_path"""
        try:           
            # Direct path access
            item = await self._msgraph_client.drives.by_drive_id(drive_id).root \
            .with_url(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{item_path}") \
            .get()
            
            return item            
        except Exception as e:
            print(f"Error getting item at path '{item_path}': {e}")
            return None
        
    async def get_item_by_id(self, drive_id : str, item_id : str):
        """Returns the object with matching item_id"""
        try:
            return await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).get()
        except Exception as e:
            print(f"Error getting item id: '{item_id}': {e}")


    async def create_folder(self, drive_id : str, parent_folder_id : str, new_folder_name : str):
        request_body = DriveItem(
            name = new_folder_name,
            folder = Folder(
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        try:
            await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id).children.post(request_body)
        except Exception as e:
            print(f"Error creating folder: {e}")

    async def delete_item(self, drive_id : str, item_id : str):
        try:
            await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).delete()
        except Exception as e:
            print(f"Error deleting item id: '{item_id}': {e}")


    async def move_item(self, drive_id : str,  item_id : str, new_location_id):
        request_body = DriveItem(
            parent_reference = ItemReference(
                id = new_location_id,
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        try:
            await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).patch(request_body)
        except Exception as e:
            print(f"Error moving item id: '{item_id}': {e}")

        




