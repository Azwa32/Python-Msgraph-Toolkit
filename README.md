# Python Microsoft Graph Toolkit

A modern, developer-friendly Python client for Microsoft Graph API that simplifies working with Microsoft 365 services.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#the-problem">The Problem</a></li>
        <li><a href="#the-solution">The Solution</a></li>
        <li><a href="#key-features">Key Features</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configuration">Configuration</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

### The Problem

The official `msgraph-sdk-python` is powerful but comes with significant challenges:
- **Auto-generated code** that's verbose and difficult to navigate
- **Complex API** with steep learning curve
- **Inconsistent patterns** across different Microsoft 365 services
- **No built-in error handling** for common scenarios

### The Solution

Python Microsoft Graph Toolkit provides a clean, intuitive wrapper around the Microsoft Graph API that:
- **Simplifies common operations** - Turn 20 lines of SDK code into 2
- **Business-focused API** - Methods designed for real-world workflows
- **Async-first architecture** - Built for modern Python applications
- **Comprehensive error handling** - Meaningful exceptions with clear messages
- **Production-ready patterns** - Configuration management, logging
- **Domain-organized services** - Logical grouping (SharePoint, Outlook, Teams, Users)

### Key Features

- ✅ **Simple API** - Clean, intuitive methods for common operations
- ✅ **Async/Await** - Modern async patterns throughout
- ✅ **Type Hints** - Full type safety for better IDE support
- ✅ **Custom Exceptions** - Meaningful error hierarchy (ValidationError, AuthenticationError, RateLimitError, etc.)
- ✅ **Service Layer** - Organized by domain (SharePoint, Outlook, Teams, Users)
- ✅ **Configuration Management** - Environment-based setup with .env support
- ✅ **Logging Integration** - Built-in logging for debugging and monitoring
- ✅ **Comprehensive Coverage** - 44+ methods across multiple Microsoft 365 services

### Services Included

**SharePoint**
- Sites management (list, get, create)
- Drive operations (list, get, copy)
- File operations (upload, download, move, delete)

**Outlook**
- Email operations (send, reply, forward, list, search)
- Calendar management (events, create, update, delete)

**Teams**
- Chat operations (create, list messages, send messages)

**Users**
- User management (list, get, search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][python.org]][python-url]
* [![Microsoft Graph][msgraph]][msgraph-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python 3.11 or higher
* Azure AD App Registration with Microsoft Graph API permissions
* Microsoft 365 tenant

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/Azwa32/python-msgraph-toolkit.git
   cd python-msgraph-toolkit
   ```

2. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the project root:
   ```env
   # Azure Authentication
   MSGRAPH_TENANT_ID=""
   MSGRAPH_CLIENT_ID=""
   MSGRAPH_API_KEY=""
   
   # SharePoint Test Variables
   TEST_SHAREPOINT_SITE_NAME=""
   TEST_SHAREPOINT_SITE_ID=""
   TEST_SHAREPOINT_DRIVE_ID=""
   TEST_SHAREPOINT_PARENT_FOLDER_ID=""
   TEST_SHAREPOINT_ITEM_NAME=""
   TEST_SHAREPOINT_ITEM_PATH=""
   TEST_SHAREPOINT_ITEM_ID=""
   
   # Outlook Test Variables
   TEST_OUTLOOK_PARENT_FOLDER_ID=""
   TEST_OUTLOOK_TO_RECIPIENT=""
   TEST_OUTLOOK_BCC_RECIPIENT=""
   TEST_OUTLOOK_REPLY_TO_RECIPIENT=""
   TEST_OUTLOOK_MESSAGE_ID=""
   TEST_OUTLOOK_MESSAGE_ID_TO_DELETE=""
   TEST_EVENT_START_DATETIME=""
   TEST_EVENT_END_DATETIME=""
   TEST_EVENT_ATTENDEE_EMAIL=""
   TEST_EVENT_ID=""
   TEST_EVENT_NEW_START_DATETIME=""
   TEST_EVENT_NEW_END_DATETIME=""
   TEST_EVENT_NEW_LOCATION=""
   TEST_EVENT_NEW_ATTENDEE_EMAIL=""
   TEST_EVENT_NEW_PRE_EVENT_REMINDER=""
   TEST_EVENT_ID_TO_DELETE=""
   
   # User Test Variables
   TEST_USER_ID=""
   TEST_USER_ID_1=""
   TEST_USER_ID_2=""
   TEST_USER_EMAIL=""
   
   # Teams Test Variables
   TEST_CHAT_ID=""
   ```

2. Set up Azure AD App Registration:
   - Go to [Azure Portal](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps)
   - Create a new App Registration
   - Configure API permissions:
     - `Sites.ReadWrite.All`
     - `Files.ReadWrite.All`
     - `Mail.ReadWrite`
     - `Calendars.ReadWrite`
     - `Chat.ReadWrite`
     - `User.Read.All`
   - Generate a client secret
   - Copy Tenant ID, Client ID, and Client Secret to your `.env` file

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### Basic Setup

```python
import asyncio
from src.msgraph_api.client import GraphClient

async def main():
    # Initialize the client
    client = GraphClient(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        secret="your-client-secret"
    )
    
    # Use the services
    sites = await client.sharepoint.sites.get_all_sites()
    print(sites)

asyncio.run(main())
```

### SharePoint Examples

```python
# Get all SharePoint sites
sites = await client.sharepoint.sites.get_all_sites()

# Get site by ID
site = await client.sharepoint.sites.get_site_by_id(site_id="site-id")

# Get site by displayname
site = await client.sharepoint.sites.get_site_by_displayname(site_name=str(os.getenv("site-name")))

```

### Outlook Examples

```python
# Send an email
await client.outlook.emails.send(
    user="user@domain.com",
    to_recipients=["recipient@domain.com"],
    subject="Hello from Python!",
    body="This is a test email"
)

# Create calendar event
await client.outlook.calendar.create_event(
    user="user@domain.com",
    subject="Team Meeting",
    start="2025-12-15T10:00:00Z",
    end="2025-12-15T11:00:00Z",
    attendees=["attendee@domain.com"]
)
```

### Teams Examples

```python
# Create a chat
chat = await client.teams.chat.create_chat(
    members=["user1@domain.com", "user2@domain.com"]
)

# Send a message
await client.teams.chat.send_message(
    chat_id="chat-id",
    content="Hello team!"
)

# List messages in a chat
messages = await client.teams.chat.list_messages(
    chat_id="chat-id",
    top=50
)
```

### Error Handling

```python
from src.msgraph_api.exceptions import (
    ValidationError,
    AuthenticationError,
    SharePointError,
    OutlookError,
    TeamsError,
    RateLimitError,
    GraphAPIError
)

try:
    sites = await client.sharepoint.sites.get_all_sites()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except SharePointError as e:
    print(f"SharePoint operation failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- PROJECT STRUCTURE -->
## Project Structure

```
python-msgraph-toolkit/
├── src/
│   └── msgraph_api/
│       ├── client.py              # Main GraphClient entry point
│       ├── exceptions.py          # Custom exception hierarchy
│       ├── services/
│       │   ├── outlook/           # Email & Calendar services
│       │   │   ├── emails.py
│       │   │   ├── calendar.py
│       │   │   └── outlook_service.py
│       │   ├── sharepoint/        # SharePoint services
│       │   │   ├── sites.py
│       │   │   ├── drives.py
│       │   │   ├── files.py
│       │   │   └── sharepoint_service.py
│       │   ├── teams/             # Teams services
│       │   │   ├── chat.py
│       │   │   └── teams_service.py
│       │   └── users/             # User services
│       │       ├── users.py
│       │       └── users_service.py
│       └── utils/                 # Utility modules
│           ├── auth.py
│           ├── retry.py
│           └── pattern_id.py
├── examples/                      # Usage examples
│   ├── sharepoint_examples.py
│   ├── outlook_examples.py
│   ├── teams_examples.py
│   └── user_examples.py
├── tests/                         # Test suite
│   ├── test_sharepoint.py
│   ├── test_outlook.py
│   ├── test_teams.py
│   └── test_users.py
└── requirements.txt
```

### Architecture Highlights

**Service Layer Pattern**: Clean separation of concerns with domain-specific services

**Dependency Injection**: Services receive the Graph client as a dependency

**Error Translation**: SDK exceptions are translated to meaningful business exceptions

**Async-First**: All operations use async/await for optimal performance

**Type Safety**: Comprehensive type hints for better IDE support and fewer bugs

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[python.org]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[python-url]: https://python.org
[msgraph]: https://img.shields.io/badge/Microsoft%20Graph-0078D4?style=for-the-badge&logo=microsoft&logoColor=white
[msgraph-url]: https://learn.microsoft.com/en-us/graph/

