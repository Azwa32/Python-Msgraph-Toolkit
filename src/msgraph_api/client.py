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
        

        
        