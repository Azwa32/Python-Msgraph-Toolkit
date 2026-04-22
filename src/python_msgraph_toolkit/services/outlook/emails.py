import base64
from msgraph.graph_service_client import GraphServiceClient
from functools import wraps
import logging
import os
import mimetypes
from typing import List, Optional
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.users.item.messages.item.reply.reply_post_request_body import ReplyPostRequestBody
from msgraph.generated.users.item.messages.item.reply_all.reply_all_post_request_body import ReplyAllPostRequestBody
from msgraph.generated.users.item.messages.item.forward.forward_post_request_body import ForwardPostRequestBody
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import MessagesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.message import Message
from msgraph.generated.models.importance import Importance
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.file_attachment import FileAttachment
from ..exceptions import ValidationError, graph_exception_handler

class EmailsService:
    """Service for managing Email through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient) -> None:
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")        
        
    async def _process_attachment(self, attachment: str, ) -> FileAttachment:
        with open(attachment, "rb") as att:
            attachment_bytes = att.read().decode("utf-8")


        file_attachment = FileAttachment(
            odata_type = "#microsoft.graph.fileAttachment",
            name = os.path.basename(attachment),
            content_type = mimetypes.guess_type(attachment, strict =False)[0],
            content_bytes = base64.urlsafe_b64decode(attachment_bytes),
        )
        return file_attachment
    

    async def list_root_mail_folders(
                self,
                *,
                user : str,
        ) -> Optional[List]:

        if not user or not user.strip():
            raise ValidationError("User is required")

        try:
            result = await self._msgraph_client.users.by_user_id(user).mail_folders.get()
            if not result:
                return
            return result.value
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return None
        
        
    async def list_child_folders(
                self,
                *,
                user : str,
                parent_folder_id : str,
        ) -> Optional[List]:

        if not user or not user.strip():
            raise ValidationError("User is required")
        if not parent_folder_id or not parent_folder_id.strip():
            raise ValidationError("Mail folder ID is required")
        try:
            result = await self._msgraph_client.users.by_user_id(user).mail_folders.by_mail_folder_id(parent_folder_id).child_folders.get()
            if not result:
                return
            return result.value
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return None
    
        
    async def get_folder_by_name(
                self,
                *,
                user : str,
                target_folder_name : str,
                parent_folder_id : Optional[str] = None,
        ):
        returned_folder = None

        if not user or not user.strip():
            raise ValidationError("User is required")
        if not target_folder_name or not target_folder_name.strip():
            raise ValidationError("Folder name is required")
    
        try:
            if parent_folder_id:
                child_folders = await self.list_child_folders(user=user, parent_folder_id=parent_folder_id)
                if not child_folders:
                    return None
                for folder in child_folders:
                    if folder.display_name == target_folder_name:
                        returned_folder = folder                    
            else:
                child_folders = await self.list_root_mail_folders(user=user)
                if not child_folders:
                    return None
                for folder in child_folders:
                    if folder.display_name == target_folder_name:
                        returned_folder = folder

            return returned_folder
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return None
    
            
        
    async def get_messages_in_folder(
                self,
                *,
                user : str,
                parent_folder_id : str,
                top : Optional[int] = 10,
        ):

        if not user or not user.strip():
            raise ValidationError("User is required")
        if not parent_folder_id or not parent_folder_id.strip():
            raise ValidationError("Mail folder ID is required")
        if top is not None and top <= 0:
            raise ValidationError("top must be a positive integer")
        try:
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
		        top = top)

            request_configuration = RequestConfiguration(
                query_parameters = query_params,
            )
            result = await self._msgraph_client.users.by_user_id(user).mail_folders.by_mail_folder_id(parent_folder_id).messages.get(request_configuration = request_configuration)
            if result:
                return result.value
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return None
        
    async def send(
                self, 
                *, 
                sender : str,
                subject : Optional[str] = None,
                body : Optional[str] = None,
                to_recipients : List[str],
                cc_recipients : Optional[List[str]] = None,
                bcc_recipients : Optional[List[str]] = None,
                reply_to : Optional[List[str]] = None,
                from_address : Optional[str] = None,
                priority : Optional[Importance] = Importance.Normal,
                body_format : Optional[BodyType] = BodyType.Text,
                request_read_receipt : Optional[bool] = False,
                attachments : Optional[List[str]] = None,
        ):

            # Validate required parameters
            if cc_recipients is None:
                cc_recipients = []
            if bcc_recipients is None:
                bcc_recipients = []
            if reply_to is None:
                reply_to = [sender]
            if from_address is None:
                from_address = sender
            if attachments is None:
                attachments = []        

            
            # build list of recipient objects
            to_recipients_list = [] 
            for recipient in to_recipients:
                to_recipients_list.append(Recipient(email_address=EmailAddress(address=recipient)))

            # build list of cc recipient objects
            cc_recipients_list = []
            if cc_recipients:
                for recipient in cc_recipients:
                    cc_recipients_list.append(Recipient(email_address=EmailAddress(address=recipient)))

            # build list of bcc recipient objects
            bcc_recipients_list = []
            if bcc_recipients:
                for recipient in bcc_recipients:
                    bcc_recipients_list.append(Recipient(email_address=EmailAddress(address=recipient)))

            # build list of reply_to recipient objects
            reply_to_list = []
            if reply_to:
                for recipient in reply_to:
                    reply_to_list.append(Recipient(email_address=EmailAddress(address=recipient)))

            # build list of attachment objects
            attachments_list = []
            if attachments:
                for attachment in attachments:
                    processed_attachment = await self._process_attachment(attachment)
                    attachments_list.append(processed_attachment)
            
            request_body = SendMailPostRequestBody(
                message = Message(
                    subject = subject,
                    importance = priority,
                    body = ItemBody(
                        content_type = body_format,
                        content = body,
                    ),
                    from_ = Recipient(
                        email_address = EmailAddress(
                            address = sender,
                        ),
                    ),
                    to_recipients = to_recipients_list if to_recipients else None,
                    cc_recipients = cc_recipients_list if cc_recipients else None,
                    bcc_recipients = bcc_recipients_list if bcc_recipients else None,
                    reply_to = reply_to_list if reply_to else None,
                    is_read_receipt_requested = request_read_receipt,
                )
            )
            try:
                await self._msgraph_client.users.by_user_id(sender).send_mail.post(request_body)
                return True
            except Exception as e:
                graph_exception_handler(e, "Outlook")
                return False


    async def reply(
                self,
                *,
                sender : str,
                message_id : str,
                comment : Optional[str] = None,
                reply_to_recipient : Optional[List[str]] = None,
        ):

        # Validate required parameters
        if not sender or not sender.strip():
            raise ValidationError("Sender is required")
        if not message_id or not message_id.strip():
            raise ValidationError("Message Id is required")

        if reply_to_recipient is None:
            reply_to_recipients = []
        
        # build list of recipient objects
        reply_to_list = []
        if reply_to_recipients:
            for recipient in reply_to_recipients:
                reply_to_list.append(EmailAddress(address = recipient))

        request_body = ReplyPostRequestBody(
            message = Message(
                to_recipients = reply_to_list if reply_to_recipients else None,
            ),
            comment = comment if comment else None,        
        )
        try:
            await self._msgraph_client.users.by_user_id(sender).messages.by_message_id(message_id).reply.post(request_body)
            return True
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return False


    async def reply_all(
                self,
                *,
                sender : str,
                message_id : str,
                comment : Optional[str] = None,
                reply_to_recipients : Optional[List[str]] = None,
        ):

        # Validate required parameters
        if not sender or not sender.strip():
            raise ValidationError("Sender is required")
        if not message_id or not message_id.strip():
            raise ValidationError("Message Id is required")

        if reply_to_recipients is None:
            reply_to_recipients = []
        
        # build list of recipient objects
        reply_to_list = []
        if reply_to_recipients:
            for recipient in reply_to_recipients:
                reply_to_list.append(EmailAddress(address = recipient))
        
        request_body = ReplyAllPostRequestBody(
            message = Message(
                to_recipients = reply_to_list if reply_to_recipients else None,
            ),
            comment = comment if comment else None,        
        )
        try:
            await self._msgraph_client.users.by_user_id(sender).messages.by_message_id(message_id).reply_all.post(request_body)
            return True
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return False


    async def forward(
                self,
                *,
                sender : str,
                message_id : str,
                to_recipients : List[str],
                comment : Optional[str] = None,
        ):

        # Validate required parameters
        if not sender or not sender.strip():
            raise ValidationError("Sender is required")
        if not message_id or not message_id.strip():
            raise ValidationError("Message Id is required")
        if not to_recipients or len(to_recipients) == 0:
            raise ValidationError("At least one recipient is required")

        # build list of recipient objects
        to_recipients_list = [] 
        for recipient in to_recipients:
            to_recipients_list.append(EmailAddress(address = recipient))

        request_body = ForwardPostRequestBody(
            to_recipients = to_recipients_list if to_recipients else None,
            comment = comment if comment else None, 
        )
        try:
            await self._msgraph_client.users.by_user_id(sender).messages.by_message_id(message_id).forward.post(request_body)
            return True
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return False

    
    async def delete(
                self,
                *,
                user : str,
                message_id : str,
        ):
        # Validate required parameters
        if not user or not user.strip():
            raise ValidationError("User is required")
        if not message_id or not message_id.strip():
            raise ValidationError("Message Id is required")
        try:        
            await self._msgraph_client.users.by_user_id(user).messages.by_message_id(message_id).delete()
            return True
        except Exception as e:
            graph_exception_handler(e, "Outlook")
            return False
        