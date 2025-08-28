from msgraph import GraphServiceClient

from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError
)
   

class SitesService:
    """Service for managing SharePoint sites through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")


    async def get_all_sites(self):
        """
        #### Retreive all Sharepoint sites accessable to the authenticated user.
        
        Returns a list of all SharePoint sites available with the current access within the MS 365 tenant.This includes team, communication and other SharePoint sites. 
        Requires read permissions.

        ##### Args:
            None

        ##### Returns:
             Dict[str, str] or None: Each object in the list contains attributes such as name, id, url etc, Returns None if there is an error in the request
        
        Useage example:
        >>> sites = await sites_service.get_all_sites()
        >>> if sites:
        ...     for site in sites:
        ...         print(f"Site: {site.display_name}")
        ...         print(f"URL: {site.web_url}")
        ...         print(f"ID: {site.id}")
        """
        try:
            response =  await self._msgraph_client.sites.get_all_sites.get()
            return response.value
        except Exception as e:
            print(f"Error get_all_sites: {e}")


    async def get_site_by_id(self, site_id : str):
        """
        #### Retrieve a specific SharePoint site by its ID.
        
        ##### Args:
            site_id (str): The unique identifier for the SharePoint site
            
        ##### Returns:
            Dict[str, str] if found, contains attributes such as name, id, url etc, None if error occurs
            
        Example:
            >>> site = await sites_service.get_site_by_id("my_site_id")
            >>> print(f"Site name: {site.display_name}")
        """
        if not site_id:
            raise ValidationError("Site ID is required")
        try:
            return await self._msgraph_client.sites.by_site_id(site_id).get()
        except Exception as e:
            print(f"Error get_site_by_id: {e}")
    
    async def get_site_by_displayname(self, site_name : str):
        """
        #### Retrieve a SharePoint site by its display name.
        
        ##### Args:
            site_name (str): The display name of the SharePoint site
            
        ##### Returns:
            Dict[str, str] first site matching the display name, or None if not found
            
        Example:
            >>> site = await sites_service.get_site_by_displayname("Project Alpha")
            >>> if site:
            ...     print(f"Found site: {site.web_url}")
        """
        if not site_name:
            raise ValidationError("Site ID is required")
        try:
            all_sites = await self._msgraph_client.sites.get_all_sites.get()
            site_values = all_sites.value        
            for site in site_values:
                if site.display_name == site_name:
                    return site
        except Exception as e:
            print(f"Error get_site_id_by_name: {e}")
        return None
    
    async def get_sub_sites(self, parent_site_id : str):
        """
        #### Retrieve all subsites of a parent SharePoint site.
        
        ##### Args:
            parent_site_id (str): The unique identifier of the parent site
            
        ##### Returns:
            List of subsite Dict[str, str]
            
        Example:
            >>> subsites = await sites_service.get_sub_sites(parent_site_id)
            >>> print(f"Found {len(subsites)} subsites")
        """
        if not parent_site_id:
            raise ValidationError("Parent site ID is required")
        try:
            response =  await self._msgraph_client.sites.by_site_id(parent_site_id).sites.get()
            return response.value
        except Exception as e:
            print(f"Error get_sub_sites: {e}")

    async def get_site_drive(self, site_id : str):
        """
        #### Returns the drive object for the site

        ##### Args: 
            site_id (str): The unique identifier for the parent site.

        ##### Returns: 
            Dict[str, str] or None if not foud
        """
        if not site_id:
            raise ValidationError("Site ID is required")
        return await self._msgraph_client.sites.by_site_id(site_id).drive.get()

