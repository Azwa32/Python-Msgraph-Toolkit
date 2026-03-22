from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.models.chat import Chat
from msgraph.generated.models.chat_type import ChatType
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember
from msgraph.generated.chats.item.messages.messages_request_builder import MessagesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody


from ..exceptions import (
    ValidationError,
    graph_exception_handler,
)

class ChatService:
    """Service for managing Teams Chat through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        
    async def list_chats(self, **kwargs):
        """List chats for the authenticated user.

        Args:
            user (str): The ID of the user whose chats to list."""
        user = kwargs.get("user") # Required
        
        if not user:
            raise ValidationError("user is required to list chats")

        try:
            result = await self._msgraph_client.users.by_user_id(user).chats.get()
            if result and result.value:
                return result.value
            return None
        except Exception as e:
            graph_exception_handler(e, "Teams")
            return None
    
        
    async def create_chat(self, **kwargs):
        """Create a new chat with specified participants.

        Args:
            members (List[str]): List of participant user IDs (minimum 2 required).
            
        Returns:
            Chat: The created chat object, or None if creation failed.
        """
        members = kwargs.get("members", []) # min 2 members required        

        if len(members) < 2:
            raise ValidationError("At least two members are required to create a chat")
        
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
            graph_exception_handler(e, "Teams")
            return None
        
    async def list_messages(self, **kwargs):
        """List messages in a specified chat.

        Args:
            chat_id (str): The ID of the chat to list messages from.
            top (int, optional): Maximum number of messages to return (default: 10).
            
        Returns:
            List[ChatMessage]: List of messages in the chat, or None if retrieval failed.
        """
        chat_id = kwargs.get("chat_id", None) # Required
        top = kwargs.get("top", 10)

        if not chat_id:
            raise ValidationError("chat_id is required to list messages in a chat")
        if top <= 0:
            raise ValidationError("top must be a positive integer")
        
        
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
            return None
        except Exception as e:
            graph_exception_handler(e, "Teams")
            return None
        
    async def send_message(self, **kwargs):
        """Send a message in a specified chat.

        Args:
            chat_id (str): The ID of the chat to send the message to.
            content (str): The content of the message to send.
            
        Returns:
            ChatMessage: The sent message object, or False if sending failed.
        """
        chat_id = kwargs.get("chat_id", None) # Required
        content = kwargs.get("content", None) # Required

        if not chat_id:
            raise ValidationError("chat_id is required to send a message in a chat")
        if not content:
            raise ValidationError("content is required to send a message in a chat")    

        request_body = ChatMessage(
            body = ItemBody(
                content = content,
            ),
        )      
        
        try:
            result = await self._msgraph_client.chats.by_chat_id(chat_id).messages.post(request_body)
            return result
        except Exception as e:
            graph_exception_handler(e, "Teams")
            return None