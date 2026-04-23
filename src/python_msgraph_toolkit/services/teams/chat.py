from typing import List, Optional
from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.models.chat import Chat
from msgraph.generated.models.chat_type import ChatType
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember
from msgraph.generated.chats.item.messages.messages_request_builder import MessagesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from ..exceptions import ValidationError, graph_exception_handler

class ChatService:
    """Service for managing Teams Chat through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient):
        self._msgraph_client = msgraph_client
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        
    async def list_chats(
                self,
                *,
                user : str,
        ):

        if not user or not user.strip():
            raise ValidationError("user is required to list chats")

        try:
            result = await self._msgraph_client.users.by_user_id(user).chats.get()
            if result and result.value:
                return result.value
            return None
        except Exception as e:
            graph_exception_handler(e, "Teams")
            return None
    
        
    async def create_chat(
                self,
                *,
                members : list[str],
        ):

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
        
    async def list_messages(
                self,
                *,
                chat_id : str,
                top : Optional[int] = 10,
        ):

        if not chat_id or not chat_id.strip():
            raise ValidationError("chat_id is required to list messages in a chat")
        if top is not None and top <= 0:
            raise ValidationError("top must be a positive integer")
        if top is not None and top > 50:
            raise ValidationError("top must be less than or equal to 50")
        
        
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(top = top)

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
        
    async def send_message(
                self,
                *,
                chat_id : str,
                content : str,
        ):

        if not chat_id or not chat_id.strip():
            raise ValidationError("chat_id is required to send a message in a chat")
        if not content or not content.strip():
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