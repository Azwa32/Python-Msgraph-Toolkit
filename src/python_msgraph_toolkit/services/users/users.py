import logging
from msgraph.graph_service_client import GraphServiceClient

from ..exceptions import ValidationError, graph_exception_handler

class UserService:
    """Service for managing Users through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        
    async def get_user(self, **kwargs):
            """Retrieve a user by their ID.

            Args:
                user_id (str): The ID of the user to retrieve.
                
            Returns:
                User: The retrieved user object, or None if not found.
            """
            user_id = kwargs.get("user_id") # required
            if not user_id:
                raise ValidationError("user_id is required")

            try:
                user = await self._msgraph_client.users.by_user_id(user_id).get()
                if user:
                    return user
                else:
                    return None
            except Exception as e:
                graph_exception_handler(e, "Users")
                return None
            
            
    async def list_users(self):
            """List all users in the organization.

            Returns:
                List[User]: A list of user objects.
            """
            try:
                users_list = await self._msgraph_client.users.get()
                if users_list and users_list.value:
                    return users_list.value
                else:
                    return None
            except Exception as e:
                graph_exception_handler(e, "Users")
                return None
            
    async def get_user_by_email(self, **kwargs):
            """Retrieve a user by their email address.

            Args:
                email (str): The email address of the user to retrieve.
                
            Returns:
                User: The retrieved user object, or None if not found.
            """
            email = kwargs.get("email") # required
            if not email:
                raise ValidationError("email is required")

            try:
                user = await self._msgraph_client.users.by_user_id(email).get()
                if user:
                    return user
                else:
                    return None
            except Exception as e:
                graph_exception_handler(e, "Users")
                return None