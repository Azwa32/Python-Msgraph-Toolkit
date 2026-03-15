from azure.identity.aio import ClientSecretCredential
from msgraph.graph_service_client import GraphServiceClient
from ..services.teams.teams_service import TeamsService
from ..services.users.users_service import UsersService
from ..services.sharepoint.sharepoint_service import SharepointService
from ..services.outlook.outlook_service import OutlookService
import logging

logger = logging.getLogger('azure')
logger.setLevel(logging.WARNING)

class Auth:
    def __init__(self, tenant_id: str, client_id: str, secret: str):
        self.scopes = ['https://graph.microsoft.com/.default']
        if not tenant_id:
            raise ValueError("Tenant ID must be supplied")
        self.tenant_id = tenant_id
        
        if not client_id:
            raise ValueError("Client ID must be supplied")
        self.client_id = client_id
        
        if not secret:
            raise ValueError("Secret must be supplied")
        self.secret = secret

        ## Initialize the authenticated Graph client 
        try: 
            credendial = ClientSecretCredential(self.tenant_id, self.client_id, self.secret)
            self._msgraph_client = GraphServiceClient(credentials=credendial, scopes=self.scopes)
        except Exception as e:
            logger.error(f"Failed to initialise GraphAPI: {e}")
            raise