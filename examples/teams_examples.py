from dotenv import load_dotenv
from ..src.msgraph_api.client import GraphClient
from pathlib import Path
import sys
import os
import asyncio

# Add src/ to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Absolute imports from your package
from ..src.msgraph_api.exceptions import (
    ValidationError,
    AuthenticationError,
    RateLimitError,
)

# create new graph instance


# await must be run within asyncio function. 
# If calls are to be run sequentially all await functions need to be inside the same await function
async def main():

    try:
        load_dotenv()
        client = GraphClient(
            str(os.getenv("MSGRAPH_TENANT_ID")),
            str(os.getenv("MSGRAPH_CLIENT_ID")),
            str(os.getenv("MSGRAPH_API_KEY"))
            )
        
    # Example: List Teams chats for a user
        user_id = os.getenv("TEST_USER_ID")
        chats = await client.teams.chat.list_chats(user=user_id)
        if chats:
            for chat in chats:
                print(f"Chat ID: {chat.id}, Topic: {chat.topic}")   

    # Example: List messages in chat
        chat_id = os.getenv("TEST_CHAT_ID")
        messages = await client.teams.chat.list_messages(chat_id=chat_id) 
        if messages:
            for message in messages:
                print(f"Message ID: {message.id}, Content: {message.body.content if message.body else 'No Content'}")
        

    except (ValidationError, AuthenticationError, RateLimitError) as e:
        print(f"❌Test Error: {e}")  # Just print the clean error message, no traceback
    except Exception as e:
        print(f"💥Unexpected test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())