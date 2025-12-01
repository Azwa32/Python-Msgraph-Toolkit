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
    
        # to run: python -m python-msgraph-toolkit.tests.user_examples
        test_email = "amitchell@focusav.com.au"

        # get all users ########################
        #users =  await client.users.users.list_users()
        #if users:
        #    for user in users:
        #        print(user.display_name, user.id)

        # get user by id ########################
        user = await client.users.users.get_user_by_email(email=test_email) 
        if user:
            print(user.display_name)

    except (ValidationError, AuthenticationError, RateLimitError) as e:
        print(f"❌Test Error: {e}")  # Just print the clean error message, no traceback
    except Exception as e:
        print(f"💥Unexpected test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())