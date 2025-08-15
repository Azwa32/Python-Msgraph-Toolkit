from msgraph import GraphServiceClient
   

class SitesService:
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")


    async def get_all_sites(self):
        try:
            return await self._msgraph_client.sites.get_all_sites.get()
        except Exception as e:
            print(f"Error get_all_sites: {e}")


    async def get_site_by_id(self, site_id : str):
        try:
            return await self._msgraph_client.sites.by_site_id(site_id).get()
        except Exception as e:
            print(f"Error get_site_by_id: {e}")
    
    async def get_site_by_displayname(self, site_name : str):
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
        try:
            return await self._msgraph_client.sites.by_site_id(parent_site_id).sites.get()
        except Exception as e:
            print(f"Error get_sub_sites: {e}")

    async def get_site_drive(self, site_id : str):
        return await self._msgraph_client.sites.by_site_id(site_id).drive.get()

