from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from msgraph.generated.models.item_reference import ItemReference
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.drives.item.items.items_request_builder import ItemsRequestBuilder 
from msgraph.generated.drives.item.items.item.children.children_request_builder import ChildrenRequestBuilder
from msgraph.generated.drives.item.search_with_q.search_with_q_request_builder import SearchWithQRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
import logging

from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError,
    Graph
)

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
    def _exceed_drive_query(self) -> RequestConfiguration:
        """For exceeding the return limit of the graph api without using pagenation"""
        drive_query_size = 1000
        query_params = ItemsRequestBuilder .ItemsRequestBuilderGetQueryParameters(
		    top = drive_query_size          
            )
        request_configuration = RequestConfiguration(
            query_parameters = query_params,
            )
        return request_configuration
        

    async def list_folder_contents(self, **kwargs):
        """
        Retrieve all items (files and folders) within a specified folder.
            
        #### Args:
            drive_id (str): SharePoint drive identifier
            parent_folder_id (str): Parent folder identifier ('root' for root directory)
            
        #### Returns:
            List[DriveItem]: List of folder contents, empty list if none found
            
        #### Raises:
            ValidationError: If drive_id or parent_folder_id is missing/invalid
            SharePointError: If access denied or other SharePoint errors
            RateLimitError: If API rate limit exceeded
            
        #### Example:
            >>> contents = await file_service.list_folder_contents(
            ...     drive_id="drive123", 
            ...     parent_folder_id="folder456"
            ... )
            >>> for item in contents:
            ...     print(f"{item.name} ({item.size} bytes)")
        """
        drive_id = kwargs.get("drive_id", None)
        parent_folder_id = kwargs.get("parent_folder_id", None)

        if not drive_id:
            raise ValidationError("Drive ID is required, Enter the correct drive ID and try again")
        if not parent_folder_id:
            raise ValidationError("Parent folder ID is required, Enter the correct parent folder & try again")
        
        try:
            response =  await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id)\
                .children.get(request_configuration = self._exceed_drive_query()) 
            return response.value if response and response.value else [] 
            
        except Exception as e:
            
            error_str = str(e).lower()
        
            # Handle drive ID invalid
            if any(validation_indicator in error_str for validation_indicator in [
                'does not represent a valid drive', 'drive id appears to be malformed',
            ]):
                raise ValidationError(f"Invalid Drive ID string: '{drive_id}'. Verify the drive ID is correct and try again.") from e
        
            # Handle parent folder ID invalid
            elif any(not_found_indicator in error_str for not_found_indicator in [
                'not found', 'does not exist', 'itemnotfound'
            ]):
                raise ValidationError(f"Parent Folder ID string: '{parent_folder_id}' invalid, folder not found. Verify the Parent Folder ID and try again ") from e
                
            # Handle access denied
            elif any(access_indicator in error_str for access_indicator in [
                'forbidden', '403', 'access denied', 'insufficient privileges'
            ]):
                raise SharePointError(f"Access denied to drive {drive_id} or folder {parent_folder_id}") from e
                
            # Handle rate limiting
            elif any(rate_indicator in error_str for rate_indicator in [
                'rate limit', 'too many requests', '429', 'throttled'
            ]):
                raise RateLimitError(f"Rate limit exceeded when accessing drive {drive_id}") from e
                
            # Generic SharePoint error for anything else
            else:
                raise SharePointError(f"Unknown sharepoint error: {e}")
        

    async def get_item_by_name(self, **kwargs):
        """
        Retrieve a specific file or folder by exact name within a parent folder.

        #### Args:
            drive_id (str): SharePoint drive identifier
            parent_folder_id (str): Parent folder identifier to search within
            item_name (str): Exact name of the file or folder to find

        #### Returns:
            DriveItem | None: First matching item found, None if not found

        #### Raises:
            ValidationError: If required parameters are missing
            AuthenticationError: If authentication fails
            SharePointError: If access denied or other SharePoint errors

        #### Example:
            >>> item = await file_service.get_item_by_name(
            ...     drive_id="drive123", 
            ...     parent_folder_id="folder456",
            ...     item_name="report.pdf"
            ... )
            >>> if item:
            ...     print(f"Found: {item.name} (Size: {item.size})")
        """
        drive_id = kwargs.get("drive_id", None)
        parent_folder_id = kwargs.get("parent_folder_id", None)
        item_name = kwargs.get("item_name", None)

        if not drive_id:
            raise ValidationError("Drive ID is required")
        if not parent_folder_id:
            raise ValidationError("Parent folder ID is required")
        if not item_name:
            raise ValidationError("Item name is required")
            
        query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(
            filter=f"name eq '{item_name}'"
        )
        request_config = RequestConfiguration(query_parameters=query_params)                
        try:
            response = await self._msgraph_client.drives.by_drive_id(drive_id)\
                .items.by_drive_item_id(parent_folder_id).children.get(request_config) 
            if response and response.value and len(response.value) > 0:          
                return response.value[0]
            return None            
        except Exception as e:
            logger.error(f"Failed to get item by name '{item_name}': {e}", exc_info=True)
            error_str = str(e).lower()
            
            if any(auth_indicator in error_str for auth_indicator in [
                'aadsts', 'invalid_client', 'unauthorized', 'authentication'
            ]):
                raise AuthenticationError(f"Authentication failed when searching for item '{item_name}'") from e
            elif any(validation_indicator in error_str for validation_indicator in [
                'malformed', 'invalid', 'invalidrequest', 'bad request'
            ]):
                raise ValidationError(f"Invalid parameters when searching for item '{item_name}'") from e
            else:
                raise SharePointError(f"Failed to get item '{item_name}': {str(e)}") from e


    async def get_item_by_path(self, **kwargs):
        """
        Retrieve a file or folder by its full path within the drive.
        
        Direct access to an item using its complete path from the drive root.
        More efficient than searching by name when you know the full path structure.

        #### Args:
            drive_id (str): The unique identifier for the SharePoint drive
            item_path (str): The full path to the item (e.g., '/Documents/Projects/file.pdf')

        #### Returns:
            Dict[str, Any] or None: Item object with full metadata, or None if not found

        #### Example:
        >>> item = await file_service.get_item_by_path(drive_id, "/Documents/report.pdf")
        >>> if item:
        ...     print(f"Found at path: {item.name}")
        """
        drive_id = kwargs.get("drive_id", None)
        item_path = kwargs.get("item_path", None)
        
        if not drive_id:
            raise ValidationError("Drive ID is required")
        if not item_path:
            raise ValidationError("Item path is required")
        try:           
            # Direct path access
            item = await self._msgraph_client.drives.by_drive_id(drive_id).root \
            .with_url(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{item_path}") \
            .get()
            
            return item            
        except Exception as e:
            print(f"Error getting item at path '{item_path}': {e}")
            return None
        
    async def get_item_by_id(self, **kwargs):
        """
        Retrieve a specific file or folder by its unique identifier.
        
        Direct access to an item using its Microsoft Graph item ID. Most efficient method
        when you have the item's unique identifier.

        #### Args:
            drive_id (str): The unique identifier for the SharePoint drive
            item_id (str): The unique identifier for the specific item

        #### Returns:
            Dict[str, Any] or None: Item object with complete metadata, or None if error occurs

        #### Example:
        >>> item = await file_service.get_item_by_id(drive_id, "01ABCDEF123456789")
        >>> if item:
        ...     print(f"Item: {item.name} (Modified: {item.last_modified_date_time})")
        """
        drive_id = kwargs.get("drive_id", None)
        item_id = kwargs.get("item_id", None)

        if not drive_id:
            raise ValidationError("Drive ID is required")
        if not item_id:
            raise ValidationError("Item ID is required")
        try:
            return await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).get()
        except Exception as e:
            print(f"Error getting item id: '{item_id}': {e}")


    async def create_folder(self, **kwargs):
        """
        Create a new folder within a specified parent directory.
        
        Creates a new folder with the specified name in the target parent folder.
        Operation will fail if a folder with the same name already exists.

        #### Args:
            drive_id (str): The unique identifier for the SharePoint drive
            parent_folder_id (str): The unique identifier for the parent folder ('root' for root directory)
            new_folder_name (str): The name for the new folder to create

        #### Returns:
            None: Operation succeeds silently or prints error message

        #### Example:
        >>> await file_service.create_folder(drive_id, parent_folder_id, "New Project Folder")
        >>> print("Folder created successfully")
        """
        drive_id = kwargs.get("drive_id", None)
        parent_folder_id = kwargs.get("parent_folder_id", None)
        new_folder_name = kwargs.get("new_folder_name", None)

        if not drive_id:
            raise ValidationError("Drive ID is required")
        if not parent_folder_id:
            raise ValidationError("Parent folder ID is required")
        if not new_folder_name:
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
            await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_folder_id).children.post(request_body)
        except Exception as e:
            print(f"Error creating folder: {e}")

            

    async def delete_item(self, **kwargs):
        """
        Permanently delete a file or folder from the drive.
        
        Removes the specified item from SharePoint. For folders, this will delete
        all contained files and subfolders. This action cannot be undone.

        #### Args:
            drive_id (str): The unique identifier for the SharePoint drive
            item_id (str): The unique identifier for the item to delete

        #### Returns:
            None: Operation succeeds silently or prints error message
            
        ⚠️ Warning: This permanently deletes the item and all its contents
            
        Usage example:
        >>> await file_service.delete_item(drive_id, item_id)
        >>> print("Item deleted successfully")
        """
        drive_id = kwargs.get("drive_id", None)
        item_id = kwargs.get("item_id", None)

        if not drive_id:
            raise ValidationError("Drive ID is required")
        if not item_id:
            raise ValidationError("Item ID is required")
        try:
            await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).delete()
        except Exception as e:
            print(f"Error deleting item id: '{item_id}': {e}")


    async def move_item(self, **kwargs):
        """
        Move a file or folder to a different location within the same drive.
        
        Relocates the specified item to a new parent folder. The item retains its
        name and properties but changes its location in the folder hierarchy.

        #### Args:
            drive_id (str): The unique identifier for the SharePoint drive
            item_id (str): The unique identifier for the item to move
            new_location_id (str): The unique identifier for the destination parent folder

        #### Returns:
            None: Operation succeeds silently or prints error message
            
        Usage example:
        >>> await file_service.move_item(drive_id, item_id, new_parent_folder_id)
        >>> print("Item moved successfully")
        """
        drive_id = kwargs.get("drive_id", None)
        item_id = kwargs.get("item_id", None)
        new_location_id = kwargs.get("new_location_id", None)

        request_body = DriveItem(
            parent_reference = ItemReference(
                id = new_location_id,
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        if not drive_id:
            raise ValidationError("Drive ID is required")
        if not item_id:
            raise ValidationError("Item ID is required")
        if not new_location_id:
            raise ValidationError("New location ID is required")
        try:
            await self._msgraph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).patch(request_body)
        except Exception as e:
            print(f"Error moving item id: '{item_id}': {e}")

        




