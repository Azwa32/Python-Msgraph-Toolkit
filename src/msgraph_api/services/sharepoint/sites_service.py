from msgraph import GraphServiceClient
import asyncio
   

class SitesService:
    def __init__(self, graph_client: GraphServiceClient):
        self.graph_client = graph_client
        if not graph_client:
            raise ValueError("msgraph client must be supplied")


    async def get_all_sites(self):
        return await self.graph_client.sites.get_all_sites.get()


    async def get_site_by_id(self, site_id):
        return await self.graph_client.sites.by_site_id(site_id).get()
    
    async def get_site_id_by_name(self, site_name):
        all_sites = await self.graph_client.sites.get_all_sites.get()
        site_values = all_sites.value        
        for site in site_values:
            if site.display_name == site_name:
                return site.id
        return None

