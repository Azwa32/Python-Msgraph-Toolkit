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

   ```sh
   pip install "git+https://github.com/Azwa32/python-msgraph-toolkit.git"
   ```




Set up Azure AD App Registration:
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
from python_msgraph_toolkit import GraphClient

client = GraphClient(
    "MSGRAPH_TENANT_ID",
    "MSGRAPH_CLIENT_ID",
    "MSGRAPH_SECRET"
)

async def main():
    root = await client.sharepoint.drives.get_drive_root_folder()
    print(f"Root folder: {root.name}")

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

### Testing

1. Create a `.env` file in the project root:
   ```env
   # Azure Authentication
   MSGRAPH_TENANT_ID=""
   MSGRAPH_CLIENT_ID=""
   MSGRAPH_SECRET=""
   
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

### Architecture Highlights

**Service Layer Pattern**: Clean separation of concerns with domain-specific services

**Dependency Injection**: Services receive the Graph client as a dependency

**Error Translation**: SDK exceptions are translated to meaningful business exceptions

**Async-First**: All operations use async/await for optimal performance

**Type Safety**: Comprehensive type hints for better IDE support and fewer bugs

**Kwargs**: kwargs used instead on typed dict to aid readability, use of arguments without extra class (TypedDict) and to reduce breaking changes if new args added.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[python.org]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[python-url]: https://python.org
[msgraph]: https://img.shields.io/badge/Microsoft%20Graph-0078D4?style=for-the-badge&logo=microsoft&logoColor=white
[msgraph-url]: https://learn.microsoft.com/en-us/graph/

