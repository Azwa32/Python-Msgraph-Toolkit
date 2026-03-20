from msgraph import GraphServiceClient
from .users import UserService
import re


class UsersService():
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
        # Initialize sub-services
        self.users = UserService(self._msgraph_client)