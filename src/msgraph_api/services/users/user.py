import logging
from msgraph.graph_service_client import GraphServiceClient

from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError,
)

class UserService:
    """Service for managing Users through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValueError("msgraph client must be supplied")
        
    def _exception_helper(self, exception : Exception) -> None:
        self.logger.error(f"SharePoint operation failed: {exception}", exc_info=True)
        error_str = str(exception).lower()
        # Handle specific Azure AD errors
        if '900023' in error_str or 'aadsts90002' in error_str:
            raise AuthenticationError("Invalid Tenant ID. Verify MSGRAPH_TENANT_ID and try again") from exception
        
        elif '700016' in error_str or 'aadsts700016' in error_str:
            raise AuthenticationError("Invalid Client ID. Verify MSGRAPH_CLIENT_ID and try again") from exception
        
        elif '7000215' in error_str or 'aadsts7000215' in error_str:
            raise AuthenticationError("Invalid Client Secret. Verify MSGRAPH_API_KEY and try again") from exception
        
        elif 'not found' in error_str or '404' in error_str:
            raise SharePointError("SharePoint resource not found") from exception
        
        elif 'forbidden' in error_str or '403' in error_str:
            raise SharePointError("Access denied to SharePoint resource") from exception
        
        elif 'rate limit' in error_str or '429' in error_str:
            raise RateLimitError("API rate limit exceeded") from exception
        
        else:
            raise SharePointError(f"SharePoint operation failed: {exception}") from exception
        
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
                self._exception_helper(e)
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
                self._exception_helper(e)
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
                self._exception_helper(e)
                return None