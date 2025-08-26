"""
msgraph_wrapper.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the set of MS Graph API wrapper exceptions.
"""
class GraphAPIError(Exception):
    """Base class for all Graph API exceptions.
    
    Attributes:
        message: The error message
        status_code: HTTP status code (if available)
        response: The HTTP response object (if available)
    """

    def __init__(self, message=None, status_code=None, response=None):
        self.message = message or "An error occurred in the Microsoft Graph API."
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class AuthenticationError(GraphAPIError):
    """An authentication error occurred."""

class ConfigurationError(GraphAPIError):
    """A configuration error occurred."""

class SharePointError(GraphAPIError):
    """A SharePoint error occurred."""

class OutlookError(GraphAPIError):
    """A Outlook error occurred."""

class TeamsError(GraphAPIError):
    """A Teams error occurred."""

class TimeoutError(GraphAPIError):
    """A timeout error occurred while making a request."""

class ConnectionError(GraphAPIError):
    """A connection error occurred while making a request."""

class RateLimitError(GraphAPIError):
    """API rate limit exceeded."""

class ValidationError(GraphAPIError):
    """Input validation failed."""

# error handling https://learn.microsoft.com/en-us/graph/errors