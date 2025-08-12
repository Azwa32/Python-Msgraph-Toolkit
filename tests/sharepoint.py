import os
from ..src.msgraph_api.client import GraphClient

if __name__ == "__main__":
    from dotenv import load_dotenv
    import asyncio
    load_dotenv() 


    client = GraphClient(
        os.getenv("MSGRAPH_TENANT_ID"),
        os.getenv("MSGRAPH_CLIENT_ID"),
        os.getenv("MSGRAPH_API_KEY")
        )
    
    drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
    location_id = "01CYM3L6TXOA256KAH4ZFLRHLVPZQ4HNJD"
    folder_name = "New folder totally not AI"
    #client.sharepoint.create_folder(drive_id, location_id, folder_name)
    
    asyncio.run(client.sharepoint.sites.get_all_sites())