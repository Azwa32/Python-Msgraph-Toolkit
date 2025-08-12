from msgraph import GraphServiceClient
   

class SitesService:
    def __init__(self, graph_client: GraphServiceClient):
        self.graph_client = graph_client
        if not graph_client:
            raise ValueError("msgraph client must be supplied")


    async def get_all_sites(self):
        response = await self.graph_client.sites.get_all_sites.get()
        children = response.value                                 # pulls values from the graph api response
        for child in children:    
            print(child.name)
