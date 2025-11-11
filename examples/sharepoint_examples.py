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

        drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
        location_id = "01CYM3L6TXOA256KAH4ZFLRHLVPZQ4HNJD"
        folder_name = "New folder totally not AI"
        #client.sharepoint.create_folder(drive_id, location_id, folder_name) 
        #########################   
        #all_sites = await client.sharepoint.sites.get_all_sites()
        #for entry in all_sites:    
        #   print(f"{entry.name} | {entry.web_url} | {entry.id}")
        ###########################   
        # graph api has built in error handling for incorrect credentials
        site = await client.sharepoint.sites.get_site_by_displayname(site_name=str(os.getenv("TEST_SHAREPOINT_SITE_NAME")))
        #print(site.id)
        #########################
        #site = await client.sharepoint.sites.get_site_by_id(site.id)
        #print(site.display_name)
        #########################
        #children = await client.sharepoint.sites.get_sub_sites(site.id)
        #for child in children:
            #print(child.display_name)
        #########################
        if site.id: # type: ignore
            drive = await client.sharepoint.sites.get_site_drive(site_id=site.id) # type: ignore
        #print(drive.name)
        #########################
        if drive.id: # type: ignore
            root_folder = await client.sharepoint.drives.get_drive_root_folder(drive_id=drive.id) # type: ignore
        #print(root_folder.name)
        #########################
        if root_folder and drive.id: # type: ignore
            items = await client.sharepoint.files.list_folder_contents(drive_id=drive.id, parent_folder_id=root_folder.id) # type: ignore
            if items:
                for item in items:
                    print(item.name, item.id, item.web_url)
        ########################
        #item = await client.sharepoint.files.get_item_by_name(drive.id, "01CYM3L6UNFXI2DU5DZJBYGQRRMAO3RSB2", "Everett Smith EQ6 HUB Equipment Register.xlsx")
        #if item:
            #print(item.name)
        ########################
        #item = await client.sharepoint.files.get_item_by_path(drive.id, "Clients/1- Current Projects/ESCO - EQ6 [9TE] - The Hub - Master Folder/Everett Smith EQ6 HUB Equipment Register.xlsx")
        #if item:
            #print(item.name)
        ########################
        # get item by id
        #item = await client.sharepoint.files.get_item_by_id(drive.id, "01CYM3L6WTDWTOTVO7LJFIWF7PZKHWK7UF")
        #print(item.name)
        ########################
    except (ValidationError, AuthenticationError, SharePointError, RateLimitError) as e:
        print(f"❌Test Error: {e}")  # Just print the clean error message, no traceback
    except Exception as e:
        print(f"💥Unexpected test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

