import base64
from msgraph import GraphServiceClient
from functools import wraps
import logging
import os
import mimetypes
from typing import List, Optional
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.importance import Importance
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.file_attachment import FileAttachment

from ...exceptions import (
    SharePointError, 
    ValidationError, 
    GraphAPIError,
    AuthenticationError,
    RateLimitError,
)

class EmailsService:
    """Service for managing Email through Microsoft Graph API."""
    def __init__(self, msgraph_client: GraphServiceClient) -> None:
        self._msgraph_client = msgraph_client
        self.logger = logging.getLogger(__name__)
        if not msgraph_client:
            raise ValidationError("msgraph client must be supplied")
        
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
    

    async def list_root_mail_folders(self, **kwargs):
        user = kwargs.get("user") # required

        if not user:
            raise ValidationError("User is required")

        result = await self._msgraph_client.users.by_user_id(user).mail_folders.get()
        if result:
            return result.value
        
        
    async def list_child_folders(self, **kwargs):
        user = kwargs.get("user") # required
        folder_id = kwargs.get("folder_id") # required

        if not user:
            raise ValidationError("User is required")
        if not folder_id:
            raise ValidationError("Mail folder ID is required")
        
        result = await self._msgraph_client.users.by_user_id(user).mail_folders.by_mail_folder_id(folder_id).child_folders.get()
        if result:
            return result.value
        
    async def get_folder_by_name(self, **kwargs):
        user = kwargs.get("user") # required
        target_folder_name = kwargs.get("target_folder_name") # required
        parent_folder_id = kwargs.get("parent_folder_id")

        if not user:
            raise ValidationError("User is required")
        if not target_folder_name:
            raise ValidationError("Folder name is required")
    

        if parent_folder_id:
            child_folders = await self.list_child_folders(user=user, folder_id=parent_folder_id)
            if child_folders:
                for folder in child_folders:
                    if folder.display_name == target_folder_name:
                        return folder.id

            
        
    
        
        
    async def list_messages_in_folder(self, **kwargs):
        user = kwargs.get("user") # required
        mailFolderId = kwargs.get("mailFolderId") # required

        if not user:
            raise ValidationError("User is required")
        if not mailFolderId:
            raise ValidationError("Mail folder ID is required")
        
        result = await self._msgraph_client.users.by_user_id(user).mail_folders.by_mail_folder_id(mailFolderId).messages.get()
        if result:
            return result.value




    async def send(self, **kwargs):
        subject = kwargs.get("subject", "No Subject")
        body = kwargs.get("body", "")
        sender = kwargs.get("sender") # required
        to_recipients = kwargs.get("to_recipients", []) # required
        cc_recipients = kwargs.get("cc_recipients", [])
        bcc_recipients = kwargs.get("bcc_recipients", [])
        reply_to = kwargs.get("reply_to", [])
        priority = kwargs.get("priority", Importance.Normal)
        body_format = kwargs.get("body_format", BodyType.Text)
        request_read_receipt = kwargs.get("request_read_receipt", False)
        attachments = kwargs.get("attachments", []) # file paths

        # Validate required parameters
        if not sender:
            raise ValidationError("Sender is required")
        if not to_recipients or len(to_recipients) == 0:
            raise ValidationError("At least one recipient is required")

        
        # build list of recipient objects
        to_recipients_list = [] 
        for recipient in to_recipients:
            to_recipients_list.append(EmailAddress(address = recipient))

        # build list of cc recipient objects
        cc_recipients_list = []
        if cc_recipients:
            for recipient in cc_recipients:
                cc_recipients_list.append(EmailAddress(address = recipient))

        # build list of bcc recipient objects
        bcc_recipients_list = []
        if bcc_recipients:
            for recipient in bcc_recipients:
                bcc_recipients_list.append(EmailAddress(address = recipient))

        # build list of reply_to recipient objects
        reply_to_list = []
        if reply_to:
            for recipient in reply_to:
                reply_to_list.append(EmailAddress(address = recipient))

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

        result = await self._msgraph_client.users.by_user_id(sender).send_mail.post(request_body)
        return result



        
