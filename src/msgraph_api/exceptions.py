"""
msgraph_wrapper.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the set of MS Graph API wrapper exceptions.
"""
from typing import Optional, Dict, Any
from requests.exceptions import HTTPError
class GraphAPIError(Exception):
    """Base class for all Graph API exceptions."""
    
    
    def __init__(self, message=None, status_code=None, response=None):
        self.message = message or "An error occurred in the Microsoft Graph API."
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class AuthenticationError(GraphAPIError):
    """An authentication error occurred."""

class ValidationError(GraphAPIError):
    """Input validation failed."""
    
class SharePointError(GraphAPIError):
    """A SharePoint error occurred."""

class OutlookError(GraphAPIError):
    """A Outlook error occurred."""

class TeamsError(GraphAPIError):
    """A Teams error occurred."""

class TimeoutError(GraphAPIError):
    """A timeout error occurred while making a request."""

class RateLimitError(GraphAPIError):
    """API rate limit exceeded."""

class Graph():
    statucCodes = {
        "400" : "Code: 400,	Bad Request, Can't process the request because it's malformed or incorrect.",
        "500" : "500's desc"
    }

def graph_exception_handler(exception: Exception, service_name: str = "Graph API"):
    """Centralized exception handler for Microsoft Graph API errors."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.error(f"{service_name} operation failed: {exception}", exc_info=True)
    error_str = str(exception).lower()
    
    # Authentication errors
    if '900023' in error_str or 'aadsts90002' in error_str:
        raise AuthenticationError("Invalid Tenant ID. Verify MSGRAPH_TENANT_ID and try again")
    elif '700016' in error_str or 'aadsts700016' in error_str:
        raise AuthenticationError("Invalid Client ID. Verify MSGRAPH_CLIENT_ID and try again")
    elif '7000215' in error_str or 'aadsts7000215' in error_str:
        raise AuthenticationError("Invalid Client Secret. Verify MSGRAPH_API_KEY and try again")
    
    # Resource errors
    elif 'not found' in error_str or '404' in error_str:
        raise GraphAPIError(f"{service_name} resource not found")
    elif 'forbidden' in error_str or '403' in error_str:
        raise GraphAPIError(f"Access denied to {service_name} resource")
    elif 'rate limit' in error_str or '429' in error_str:
        raise RateLimitError("API rate limit exceeded")
    
    # Default
    else:
        raise GraphAPIError(f"{service_name} operation failed: {exception}")

# error handling https://learn.microsoft.com/en-us/graph/errors