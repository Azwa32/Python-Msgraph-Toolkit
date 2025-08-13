# msgraph API documentation https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0&preserve-view=true

from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient

#from users import UsersServices
from .services.sharepoint.sharepoint_service import SharepointService
#from outlook import OutlookService
#from teams import TeamsService

import logging
logger = logging.getLogger('azure')
logger.setLevel(logging.WARNING)

class GraphClient:
    def __init__(self, tenant_id=None, client_id=None, secret=None):
        self.scopes = ['https://graph.microsoft.com/.default']
        self.tenant_id = tenant_id
        self.graph_client = None
        if not self.tenant_id:
            raise ValueError("Tenant ID must be supplied")
        
        self.client_id = client_id
        if not self.client_id:
            raise ValueError("Client ID must be supplied")
        
        self.secret = secret
        if not self.secret:
            raise ValueError("Secret must be supplied")
        
        self._initialise_graph_client()

        # initialise child services
        self.sharepoint = SharepointService(self.graph_client)
        #self.outlook = OutlookService(self.graph_client)
        #self.teams = TeamsService(self.graph_client)
        #self.users = UserService(self.graph_client)
        
    def _initialise_graph_client(self):
        """Initialize the authenticated Graph client"""
        try: 
            credendial = ClientSecretCredential(self.tenant_id, self.client_id, self.secret)
            self.graph_client = GraphServiceClient(credentials=credendial, scopes=self.scopes)
        except Exception as e:
            logger.error(f"Failed to initialise GraphAPI: {e}")
            raise


if __name__ == "__main__":
    from dotenv import load_dotenv
    import asyncio
    import os
    load_dotenv()
    client = GraphClient(
        os.getenv("MSGRAPH_TENANT_ID"),
        os.getenv("MSGRAPH_CLIENT_ID"),
        os.getenv("MSGRAPH_API_KEY")
        )
    
    drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
    location_id = "01CYM3L6TXOA256KAH4ZFLRHLVPZQ4HNJD"
    folder_name = "New folder totally not AI"
    #client.sharepoint.create_folder(drive_id, location_id, folder_name) 
    #########################   
    #call = client.sharepoint.sites.get_all_sites()
    #response = asyncio.run(call).value
    #for entry in response:    
    #   print(f"{entry.name} | {entry.web_url} | {entry.id}")
    #########################
    #site_id = "focusav-my.sharepoint.com,6009deac-9bce-4b97-9f1f-a94ddd9dd91b,75e31673-ba64-4306-9e67-b45b080e4703"
    #call = client.sharepoint.sites.get_site_by_id(site_id)
    #response = asyncio.run(call).display_name
    #print(response)
    ###########################
    call = client.sharepoint.sites.get_site_id_by_name("Aaron Mitchelll")
    response = asyncio.run(call)
    print(response)

        

        
        