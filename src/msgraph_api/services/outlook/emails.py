from msgraph import GraphServiceClient
from functools import wraps
import logging
from typing import List, Optional
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress

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
        
    def _exception_helper(self, exception : Exception):
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
        
    async def send(self, subject_line, email_content, sender, email_address):
        """
        Send an email message through Microsoft Graph API (Application mode).
        
        This method sends an email on behalf of a specified user using application permissions.
        The email will not be saved to the sender's Sent Items folder by default.
        
        Args:
            subject_line (str): The subject line of the email message
            email_content (str): The body content of the email (plain text format)
            sender (str): The user ID or email address of the person sending the email
            email_address (str): The recipient's email address
            
        Returns:
            None: This method doesn't return a value upon successful completion
            
        Raises:
            ValidationError: If msgraph client is not supplied during initialization
            AuthenticationError: If Azure AD authentication fails (invalid tenant, client ID, or secret)
            GraphAPIError: If the email operation fails due to Graph API errors
            RateLimitError: If API rate limits are exceeded
            
        Example:
            >>> email_service = EmailsService(msgraph_client)
            >>> await email_service.send_email(
            ...     subject_line="Meeting Reminder",
            ...     email_content="Don't forget about our meeting at 2 PM today.",
            ...     sender="manager@company.com", 
            ...     email_address="employee@company.com"
            ... )
            
        Note:
            - Requires Mail.Send application permission in Azure AD
            - The sender must be a valid user in your organization
            - Email is sent as plain text (BodyType.Text)
            - Email is not saved to sender's Sent Items folder (save_to_sent_items = False)
            - This method uses application permissions, not delegated permissions         
        """
        
        request_body = SendMailPostRequestBody(
            message = Message(
                subject = subject_line,
                body = ItemBody(
                    content_type = BodyType.Text,
                    content = email_content,
                ),
                to_recipients = [
                    Recipient(
                        email_address = EmailAddress(
                            address = email_address,
                        ),
                    ),
                ],
            ),        
        save_to_sent_items = False,
        )
        await self._msgraph_client.users.by_user_id(sender).send_mail.post(request_body)
        
