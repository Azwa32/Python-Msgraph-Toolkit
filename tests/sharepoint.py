
if __name__ == "__main__":
    from dotenv import load_dotenv
    from ..src.msgraph_api.client import GraphClient
    import asyncio
    import os

    # create new graph instance
    load_dotenv()
    client = GraphClient(
        os.getenv("MSGRAPH_TENANT_ID"),
        os.getenv("MSGRAPH_CLIENT_ID"),
        os.getenv("MSGRAPH_API_KEY")
        )
    
    # await must be run within asyncio function. 
    # If calls are to be run sequentially all await functions need to be inside the same await function
    async def main():
        
        #sites
        #########################
        drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
        location_id = "01CYM3L6TXOA256KAH4ZFLRHLVPZQ4HNJD"
        folder_name = "New folder totally not AI"
        #client.sharepoint.create_folder(drive_id, location_id, folder_name) 
        #########################   
        #all_sites = await client.sharepoint.sites.get_all_sites()
        #for entry in all_sites.value:    
        #   print(f"{entry.name} | {entry.web_url} | {entry.id}")
        ###########################    
        site = await client.sharepoint.sites.get_site_by_displayname("FocusAV")
        #print(site.id)
        #########################
        #site_id = "focusav.sharepoint.com,3580de04-1622-4f4c-967d-c221f6e18144,d6842c6f-b7a9-4ea6-aa4c-15901a4ad95b"
        #site = await client.sharepoint.sites.get_site_by_id(site.id)
        #print(site.display_name)
        #########################
        #children = await client.sharepoint.sites.get_sub_sites(site.id)
        #for child in children.value:
        #    print(child.display_name)
        #########################
        drive = await client.sharepoint.sites.get_site_drive(site.id)
        #print(drive.id)
        #########################
        root_folder = await client.sharepoint.drives.get_drive_root_folder(drive.id)
        #print(root_folder.id)
        #########################
        #folders = await client.sharepoint.files.list_folders(drive.id, root_folder.id)
        #for folder in folders.value:
            #print(folder.name)
        ########################
        items = await client.sharepoint.files.get_folder_by_name(drive.id, root_folder.id, "Clients")
        for item in items:
            print(item.name)
        ########################


    asyncio.run(main())

