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

# error handling https://learn.microsoft.com/en-us/graph/errors