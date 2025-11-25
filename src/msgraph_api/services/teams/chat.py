import logging
from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.models.chat import Chat
from msgraph.generated.models.chat_type import ChatType
from msgraph.generated.models.conversation_member import ConversationMember
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember

from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError,
)

class ChatService:
    """Service for managing Teams Chat through Microsoft Graph API."""
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
        
    async def create_chat(self, **kwargs):
        """
        Create a new chat with specified participants.
        #### Args:
            participants (list): List of participant user IDs
        #### Returns:
            Chat: The created chat object, or None if creation failed
        #### Usage example:
            >>> new_chat = await chat_service.create_chat(participants=["user1_id", "user2_id"])
            >>> if new_chat:
            ...     print(f"Chat ID: {new_chat.id}")
            ...     print(f"Chat topic: {new_chat.topic}")
        """
        members = kwargs.get("members", []) # min 2 members required        

        if len(members) < 2:
            raise ValueError("At least two members are required to create a chat")
        
        # build list of members
        members_list = []
        for member in members:
            members_list.append(
                AadUserConversationMember(
                    odata_type = "#microsoft.graph.aadUserConversationMember",
                    roles = [
                        "owner",
                    ],
                    additional_data = {
                            f"user@odata_bind" : f"https://graph.microsoft.com/v1.0/users('{member}')",
                    }
                )
            )
        
        # check if chat is OnoOnOne or Group
        chat_type = ChatType.OneOnOne
        if len(members) > 2:
            chat_type = ChatType.Group        
        request_body = Chat(
            chat_type = chat_type,
            members = members_list,
        )
        try:
            chat = await self._msgraph_client.chats.post(request_body)
            return chat
        except Exception as e:
            self._exception_helper(e)
            return None
        
        