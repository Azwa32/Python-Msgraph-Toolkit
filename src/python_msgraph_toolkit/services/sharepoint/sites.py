from msgraph.graph_service_client import GraphServiceClient
import logging
from typing import List, NoReturn, Optional
from msgraph.generated.models.site import Site
from msgraph.generated.models.drive import Drive
from ..exceptions import ValidationError, graph_exception_handler

class SitesService:
    """Service for managing SharePoint sites through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient) -> None:
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        

    async def get_all_sites(self) -> List[Site]:
        """
        Retreive all Sharepoint sites accessable to the authenticated user.
        
        Returns a list of all SharePoint sites available with the current access within the MS 365 tenant.This includes team, communication and other SharePoint sites. 
        Requires read permissions.

        #### Args:
            None

        #### Returns:
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
            graph_exception_handler(e, "SharePoint")
            return [] # This line will never be reached due to exception being raised, but is here to satisfy return type
    


    async def get_site_by_id(
                self,
                *,
                site_id : str,
        ) -> Optional[Site]:

        if not site_id or not site_id.strip():
            raise ValidationError("Site ID is required")
        try:
            response = await self._msgraph_client.sites.by_site_id(site_id).get()
            return response if response else None
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return None # This line will never be reached due to exception being raised, but is here to satisfy return type
    

    async def get_site_by_displayname(
                self,
                *,
                site_name : str,
        ) -> Optional[Site]:

        if not site_name or not site_name.strip():
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
            graph_exception_handler(e, "SharePoint")
            return None # This line will never be reached due to exception being raised, but is here to satisfy return type
    

    async def get_sub_sites(
                self,
                *,
                parent_site_id : str,
        ) -> List[Site]:

        if not parent_site_id or not parent_site_id.strip():
            raise ValidationError("Parent site ID is required")
        try:
            response =  await self._msgraph_client.sites.by_site_id(parent_site_id).sites.get()
            return response.value if response.value else [] # type: ignore[attr-defined]
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return [] # This line will never be reached due to exception being raised, but is here to satisfy return type

    
    async def get_site_drive(
                self,
                *,
                site_id : str,
        ) -> Optional[Drive]:

        if not site_id or not site_id.strip():
            raise ValidationError("Site ID is required")
        try:
            response = await self._msgraph_client.sites.by_site_id(site_id).drive.get()
            return response if response else None
        except Exception as e:
            graph_exception_handler(e, "SharePoint")
            return None # This line will never be reached due to exception being raised, but is here to satisfy return type
