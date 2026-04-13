from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder, Optional
from msgraph.generated.models.item_reference import ItemReference
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.drives.item.items.items_request_builder import ItemsRequestBuilder 
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
from msgraph.generated.drives.item.search_with_q.search_with_q_request_builder import SearchWithQRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
import logging
from ..exceptions import ValidationError, graph_exception_handler

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        
    def _exceed_drive_query(self) -> RequestConfiguration:
        """For exceeding the return limit of the graph api without using pagenation"""
        drive_query_size = 1000
        query_params = ItemsRequestBuilder.ItemsRequestBuilderGetQueryParameters(
		    top = drive_query_size          
            )
        request_configuration = RequestConfiguration(
            query_parameters = query_params,
            )
        return request_configuration
        

    async def list_folder_contents(
                self,
                *,
                drive_id : str,
                parent_folder_id : str,
        ) -> list[DriveItem]:

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required, Enter the correct drive ID and try again")
        if not parent_folder_id or not parent_folder_id.strip():
            raise ValidationError("Parent folder ID is required, Enter the correct parent folder & try again")
        
        try:
            response =  await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id).children.get(request_configuration = self._exceed_drive_query()) 
            return response.value if response and response.value else []             
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return [] # This line will never be reached due to exception being raised, but is here to satisfy return type


    async def get_item_by_name(
                self,
                *,
                drive_id : str,
                parent_folder_id : str,
                item_name : str,
        ) -> Optional[DriveItem]:

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required")
        if not parent_folder_id or not parent_folder_id.strip():
            raise ValidationError("Parent folder ID is required")
        if not item_name or not item_name.strip():
            raise ValidationError("Item name is required")
            
        query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(filter=f"name eq '{item_name}'")
        request_config = RequestConfiguration(query_parameters=query_params)                
        try:
            response = await self._msgraph_client.drives.by_drive_id(drive_id)\
                .items.by_drive_item_id(parent_folder_id).children.get(request_config) 
            if response and response.value and len(response.value) > 0:          
                return response.value[0]
            return None            
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return None


    async def get_item_by_path(
                self,
                *,
                drive_id : str,
                item_path : str,
        ) -> Optional[DriveItem]:

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required")
        if not item_path or not item_path.strip():
            raise ValidationError("Item path is required")
        try:           
            # Direct path access
            item = await self._msgraph_client.drives.by_drive_id(drive_id).root \
            .with_url(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{item_path}") \
            .get()
            
            return item            
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return None
        
    async def get_item_by_id(
                self,
                *,
                drive_id : str,
                item_id : str,
        ) -> Optional[DriveItem]:

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required")
        if not item_id or not item_id.strip():
            raise ValidationError("Item ID is required")
        try:
            return await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).get()
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return None


    async def create_folder(
                self,
                *,
                drive_id : str,
                parent_folder_id : str,
                new_folder_name : str,
        ) -> Optional[DriveItem]:

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required")
        if not parent_folder_id or not parent_folder_id.strip():
            raise ValidationError("Parent folder ID is required")
        if not new_folder_name or not new_folder_name.strip():
            raise ValidationError("New folder name is required")
        request_body = DriveItem(
            name = new_folder_name,
            folder = Folder(
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        try:
            folder = await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id).children.post(request_body)
            return folder
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return None
            

    async def delete_item(
                self,
                *,
                drive_id : str,
                item_id : str,
        ):

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required")
        if not item_id or not item_id.strip():
            raise ValidationError("Item ID is required")
        try:
            await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).delete()
        except Exception as e:
            graph_exception_handler(e, "SharePoint")


    async def move_item(
                self,
                *,
                drive_id : str,
                item_id : str,
                new_location_id : str,
        ):

        if not drive_id or not drive_id.strip():
            raise ValidationError("Drive ID is required")
        if not item_id or not item_id.strip():
            raise ValidationError("Item ID is required")
        if not new_location_id or not new_location_id.strip():
            raise ValidationError("New location ID is required")
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
            graph_exception_handler(e, "SharePoint")

        




