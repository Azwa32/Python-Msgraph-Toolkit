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
        
    # to run: python -m python-msgraph-toolkit.tests.sharepointExamples

    #sites
    #########################
        #client.sharepoint.create_folder(drive_id, location_id, folder_name) 
        #########################   
        all_sites = await client.sharepoint.sites.get_all_sites()
        for entry in all_sites:    
          print(f"{entry.name} | {entry.web_url} | {entry.id}")
        ###########################   
        # graph api has built in error handling for incorrect credentials
        site = await client.sharepoint.sites.get_site_by_displayname(site_name=str(os.getenv("TEST_SHAREPOINT_SITE_NAME")))
        if site is not None:
            print(site.id)
        #########################
        if site is not None:
            site = await client.sharepoint.sites.get_site_by_id(site_id=site.id)
            print(site.display_name if site else "No site found")
        ########################
        children = await client.sharepoint.sites.get_sub_sites(site_id=str(os.getenv("TEST_SHAREPOINT_SITE_ID")))
        for child in children:
            print(child.display_name)
        #########################
        if site.id: # type: ignore
            drive = await client.sharepoint.sites.get_site_drive(site_id=site.id) # type: ignore
            print(drive.name if drive else "No drive found")
        #########################
        if drive.id: # type: ignore
            root_folder = await client.sharepoint.drives.get_drive_root_folder(drive_id=drive.id) # type: ignore
        print(root_folder.name if root_folder else "No root folder found")
        #########################
        if root_folder and drive.id: # type: ignore
            items = await client.sharepoint.files.list_folder_contents(drive_id=drive.id, parent_folder_id=root_folder.id) # type: ignore
            if items:
                for item in items:
                    print(item.name, item.id, item.web_url)
        ########################
        if root_folder and drive: # type: ignore
            item = await client.sharepoint.files.get_item_by_name(drive_id=drive.id, 
                                                                  parent_folder_id=str(os.getenv("TEST_SHAREPOINT_PARENT_FOLDER_ID")), 
                                                                  item_name=str(os.getenv("TEST_SHAREPOINT_ITEM_NAME")))
            if item:
                print(item.name)
        ########################
        if root_folder and drive: # type: ignore
            item = await client.sharepoint.files.get_item_by_path(drive_id=drive.id,
                                                                item_name=str(os.getenv("TEST_SHAREPOINT_ITEM_PATH")))
        #if item:
            #print(item.name)
        ########################
        # get item by id
        if root_folder and drive: # type: ignore
            item = await client.sharepoint.files.get_item_by_id(drive_id=drive.id, 
                                                                item_id=str(os.getenv("TEST_SHAREPOINT_ITEM_ID")))
        #print(item.name)
        ########################
    except (ValidationError, AuthenticationError, SharePointError, RateLimitError) as e:
        print(f"❌Test Error: {e}")  # Just print the clean error message, no traceback
    except Exception as e:
        print(f"💥Unexpected test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

