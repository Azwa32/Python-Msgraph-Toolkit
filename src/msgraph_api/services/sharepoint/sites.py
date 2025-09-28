from msgraph import GraphServiceClient
from functools import wraps
import logging
from typing import List, Optional
from msgraph.generated.models.site import Site
from msgraph.generated.models.drive import Drive

from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError,
)

class SitesService:
    """Service for managing SharePoint sites through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient) -> None:
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")



    def _exception_helper(self, exception : Exception):
        self.logger.error(f"SharePoint operation failed: {exception}", exc_info=True)
        error_str = str(exception).lower()
        # Handle specific Azure AD errors
        if '900023' in error_str or 'aadsts90002' in error_str:
            raise AuthenticationError("Invalid Tenant ID. Verify MSGRAPH_TENANT_ID and try again") from exception
        
        elif '700016' in error_str or 'aadsts700016' in error_str:
            raise AuthenticationError("Invalid Client ID. Verify MSGRAPH_CLIENT_ID and try again") from exception
        
        elif '7000215' in error_str or 'aadsts7000215' in error_str:
            raise AuthenticationError("Invalid Client Secret. Verify MSGRAPH_API_KEY and try again") from exception
        
        elif 'not found' in error_str or '404' in error_str:
            raise SharePointError("SharePoint resource not found") from exception
        
        elif 'forbidden' in error_str or '403' in error_str:
            raise SharePointError("Access denied to SharePoint resource") from exception
        
        elif 'rate limit' in error_str or '429' in error_str:
            raise RateLimitError("API rate limit exceeded") from exception
        
        else:
            raise SharePointError(f"SharePoint operation failed: {exception}") from exception
        

    async def get_all_sites(self) -> List[Site]:
        """
        #### Retreive all Sharepoint sites accessable to the authenticated user.
        
        Returns a list of all SharePoint sites available with the current access within the MS 365 tenant.This includes team, communication and other SharePoint sites. 
        Requires read permissions.

        ##### Args:
            None

        ##### Returns:
             Dict[str, str] or empty list: Each object in the list contains attributes such as name, id, url etc.
        
        Useage example:
        >>> sites = await sites_service.get_all_sites()
        >>> if sites:
        ...     for site in sites:
        ...         print(f"Site: {site.display_name}")
        ...         print(f"URL: {site.web_url}")
        ...         print(f"ID: {site.id}")
        """
        try:
            response = await self._msgraph_client.sites.get_all_sites.get()
            return response.value if response.value else [] # type: ignore[attr-defined]
        except Exception as e:
            self._exception_helper(e)
    


    async def get_site_by_id(self, site_id: str) -> Optional[Site]:
        """
        #### Retrieve a specific SharePoint site by its ID.
        
        ##### Args:
            site_id (str): The unique identifier for the SharePoint site
            
        ##### Returns:
            Dict[str, str] if found, contains attributes such as name, id, url etc or None if not found
            
        Example:
            >>> site = await sites_service.get_site_by_id("my_site_id")
            >>> print(f"Site name: {site.display_name}")
        """
        if not site_id:
            raise ValidationError("Site ID is required")
        try:
            response = await self._msgraph_client.sites.by_site_id(site_id).get()
            return response if response else None
        except Exception as e:
            self._exception_helper(e)
    

    async def get_site_by_displayname(self, site_name: str) -> Optional[Site]:
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
            raise ValidationError("Site Name is required")
        try:
            all_sites = await self._msgraph_client.sites.get_all_sites.get()
            if not all_sites.value: # type: ignore[attr-defined]
                return None        
            for site in all_sites.value: # type: ignore[attr-defined]
                if site.display_name and site.display_name.lower() == site_name.lower():
                    return site
            return None  # Explicit return when no match found
        except Exception as e:
            self._exception_helper(e)
    

    async def get_sub_sites(self, parent_site_id: str) -> List[Site]:
        """
        #### Retrieve all subsites of a parent SharePoint site.
        
        ##### Args:
            parent_site_id (str): The unique identifier of the parent site
            
        ##### Returns:
            List of subsite Dict[str, str] or an empty list if none found
            
        Example:
            >>> subsites = await sites_service.get_sub_sites(parent_site_id)
            >>> print(f"Found {len(subsites)} subsites")
        """
        if not parent_site_id:
            raise ValidationError("Parent site ID is required")
        try:
            response =  await self._msgraph_client.sites.by_site_id(parent_site_id).sites.get()
            return response.value if response.value else [] # type: ignore[attr-defined]
        except Exception as e:
            self._exception_helper(e)

    
    async def get_site_drive(self, site_id: str) -> Optional[Drive]:
        """
        #### Returns the drive object for the site

        ##### Args: 
            site_id (str): The unique identifier for the parent site.

        ##### Returns: 
            Dict[str, str] or None if not found
        """
        if not site_id:
            raise ValidationError("Site ID is required")
        try:
            response = await self._msgraph_client.sites.by_site_id(site_id).drive.get()
            return response if response else None
        except Exception as e:
            self._exception_helper(e)
