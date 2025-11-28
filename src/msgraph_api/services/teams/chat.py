from email import message
import logging
from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.models.chat import Chat
from msgraph.generated.models.chat_type import ChatType
from msgraph.generated.models.conversation_member import ConversationMember
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember
from msgraph.generated.chats.item.messages.messages_request_builder import MessagesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType

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
        
    async def list_messages_in_chat(self, **kwargs):
        """
        List messages in a specified chat.
        #### Args:
            chat_id (str): The ID of the chat to list messages from
        #### Returns:
            list: List of messages in the chat, or None if retrieval failed
        #### Usage example:
            >>> messages = await chat_service.list_messages_in_chat(chat_id="chat_id_here")
            >>> if messages:
            ...     for message in messages:
            ...         print(f"Message ID: {message.id}")
            ...         print(f"Message content: {message.body.content}")
        """
        chat_id = kwargs.get("chat_id", None) # Required
        top = kwargs.get("top", 10)

        if not chat_id:
            raise ValueError("chat_id is required to list messages in a chat")
        if top <= 0:
            raise ValueError("top must be a positive integer")
        
        
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
		top = top,
        )

        request_configuration = RequestConfiguration(
        query_parameters = query_params,
        )        
        try:
            result = await self._msgraph_client.chats.by_chat_id(chat_id).messages.get(request_configuration = request_configuration)
            if result and result.value:
                return result.value
        except Exception as e:
            self._exception_helper(e)
            return None
        
    async def send_message_in_chat(self, **kwargs):
        """
        Send a message in a specified chat.
        #### Args:
            chat_id (str): The ID of the chat to send the message to
            content (str): The content of the message to send
        #### Returns:
            bool: True if the message was sent successfully, False otherwise
        #### Usage example:
            >>> success = await chat_service.send_message_in_chat(chat_id="chat_id_here", content="Hello, World!")
            >>> if success:
            ...     print("Message sent successfully")
        """
        chat_id = kwargs.get("chat_id", None) # Required
        content = kwargs.get("content", None) # Required

        if not chat_id:
            raise ValueError("chat_id is required to send a message in a chat")
        if not content:
            raise ValueError("content is required to send a message in a chat")    

        request_body = ChatMessage(
            body = ItemBody(
                content = content,
            ),
        )      
        
        try:
            result = await self._msgraph_client.chats.by_chat_id(chat_id).messages.post(request_body)
            return result
        except Exception as e:
            self._exception_helper(e)
            return False