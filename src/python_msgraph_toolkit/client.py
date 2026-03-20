# msgraph API documentation https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0&preserve-view=true

from .services.teams.teams_service import TeamsService
from .services.users.users_service import UsersService
from .services.sharepoint.sharepoint_service import SharepointService
from .services.outlook.outlook_service import OutlookService
from .utils.auth import Auth

import logging
logger = logging.getLogger('azure')
logger.setLevel(logging.WARNING)

class GraphClient:
    def __init__(self, tenant_id: str, client_id: str, secret: str):
        authorised_msgraph = Auth(tenant_id, client_id, secret)
        self.authorised = False

        # initialise child services
        if authorised_msgraph and authorised_msgraph.authorised:
            self.authorised = True
            self.sharepoint = SharepointService(authorised_msgraph._msgraph_client)
            self.outlook = OutlookService(authorised_msgraph._msgraph_client)
            self.teams = TeamsService(authorised_msgraph._msgraph_client)
            self.users = UsersService(authorised_msgraph._msgraph_client)
        



        

        
        