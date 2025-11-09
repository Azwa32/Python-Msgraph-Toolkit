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
    SharePointError,
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
    
        # to run: python -m python-msgraph-toolkit.tests.outlookExamples
        user_email = "amitchell@focusav.com.au"
        target_folder = "AAMkADVhZGM3NTVhLTAwNzMtNGU4ZS1hZThhLTMwOTUzMjMyNDJjOQAuAAAAAAAiJJiCJitKQJlJc53cBcgSAQBftRv1EbWpS7ZOQzh15ab7AAAAAAEMAAA="
        
        #email
        #list root mail folders ########################
        #folders = await client.outlook.emails.list_root_mail_folders(user = user_email)
        #if folders:
        #    for folder in folders:
        #        print(folder.display_name, folder.id)

        #list child folders ########################
        folders = await client.outlook.emails.list_child_folders(user=user_email, parent_folder_id=target_folder, )
        if folders:
            for folder in folders:
                print(folder.display_name, folder.id)

        #list_messages_in_folder ########################
        

    except (ValidationError, AuthenticationError, SharePointError, RateLimitError) as e:
        print(f"❌Test Error: {e}")  # Just print the clean error message, no traceback
    except Exception as e:
        print(f"💥Unexpected test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())