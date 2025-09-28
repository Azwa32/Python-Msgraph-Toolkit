# msgraph API documentation https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0&preserve-view=true

from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient

from msgraph.generated.drives.item.items.item.copy.copy_post_request_body import CopyPostRequestBody
from msgraph.generated.models.item_reference import ItemReference
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder   
from kiota_abstractions.base_request_configuration import RequestConfiguration

from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress





import os

import logging
logger = logging.getLogger('azure')
logger.setLevel(logging.WARNING)


class GraphAPI:

    def __init__(self, config_file):
        # Load configuration from file if provided
        if config_file:
            # For now, just ignore the config_file parameter
            # You can implement YAML loading later
            pass

        # Initialise graph client and authorise. Get keys from environment, asserted as strings 
        self.TENANT_ID = str(os.getenv("MSGRAPH_TENANT_ID"))
        self.CLIENT_ID = str(os.getenv("MSGRAPH_CLIENT_ID"))
        self.SCOPES = ['https://graph.microsoft.com/.default']
        self.DRIVE_ID = str(os.getenv("MSGRAPH_DRIVE_ID"))   
        self.CLIENT_SECRET = str(os.getenv("MSGRAPH_API_KEY"))
        if not self.TENANT_ID:
            raise ValueError("Tenant ID not set. Please set the TENANT_ID environment variable.") 
        if not self.CLIENT_ID:
            raise ValueError("Client ID not set. Please set the CLIENT_ID environment variable.") 
        if not self.CLIENT_SECRET:
            raise ValueError("API key not found. Please set the MSGRAPH_API_KEY environment variable.") 
        if not self.DRIVE_ID:
            raise ValueError("Drive ID not found. Please set the DRIVE_ID environment variable.")                  
        try: 
            credendial = ClientSecretCredential(self.TENANT_ID, self.CLIENT_ID, self.CLIENT_SECRET)
            self.graph_client = GraphServiceClient(credentials=credendial, scopes=self.SCOPES)
        except Exception as e:
            logger.error(f"Failed to initialise GraphAPI: {e}")
            raise
            


    ##-- Sharepoint --##

    # for exceeding the return limit of the graph api without using pagenation
    def exceed_drive_query(self):
        drive_query_size = 1000     # this would be the most amount of customers FocusAv expects to have
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
		    top = drive_query_size          
            )
        request_configuration = RequestConfiguration(
            query_parameters = query_params,
            )
        return request_configuration



    async def copy_folder(self, TARGET_FOLDER_ID, NEW_LOCATION_ID, NEW_FOLDER_NAME):
        request_body = CopyPostRequestBody(
            # where to send the file to
            parent_reference = ItemReference(
                drive_id = self.DRIVE_ID,
                id = NEW_LOCATION_ID,
            ),
            name = NEW_FOLDER_NAME,
        )
        # where the file is from
        await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(TARGET_FOLDER_ID).copy.post(request_body)



    async def create_folder(self, new_location_id, new_folder_name):
        request_body = DriveItem(
            name = new_folder_name,
            folder = Folder(
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        # where to create the new folder
        await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(new_location_id).children.post(request_body)




    async def delete_item(self, target):
        # delete target
        await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(target).delete()

    


    async def move_item(self, target, NEW_LOCATION):
        request_body = DriveItem(
            parent_reference = ItemReference(
                id = NEW_LOCATION,
            ),
            additional_data = {
                    "@microsoft_graph_conflict_behavior" : "fail",
            }
        )
        await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(target).patch(request_body)




    async def get_folder_id_by_name(self, parent_folder_id, child_folder_name):
        response = await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(parent_folder_id).children.get(request_configuration = self.exceed_drive_query()) # type: ignore
        if response and response.value:
            values = response.value                                 # pulls values from the graph api response
            for child in values:    
                if child.name == child_folder_name:                 # finds id of a folder that matches the child folder name  
                    folder_id = child.id
                    return folder_id
            return response.value
        else:
            print(f"Folder {child_folder_name} not found.")
            



    async def get_folder_id_by_partial_name(self, parent_folder_id, partial_name):
        response = await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(parent_folder_id).children.get(self.exceed_drive_query())   # type: ignore
        if response and response.value:
            values = response.value                                 # pulls values from the graph api response
            for child in values:    
                if partial_name in child.name:                        # if JN is found in the folder name  
                    folder_id = child.id
                    return folder_id
        else:
            print(f"Folder with {partial_name} in name not found or folder {parent_folder_id} does not exist.")
            



    async def list_folders(self, parent_folder_id):
        response = await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(parent_folder_id).children.get(request_configuration = self.exceed_drive_query()) # type: ignore
        if response and response.value:
            children = response.value                                 # pulls values from the graph api response
            for child in children:    
                print(child.name)
        else:
            print(f"No children found in folder {parent_folder_id} or folder {parent_folder_id} does not exist.")

    async def folder_exists(self, parent_folder_id, child_folder_name):
        response = await self.graph_client.drives.by_drive_id(self.DRIVE_ID).items.by_drive_item_id(parent_folder_id).children.get(request_configuration = self.exceed_drive_query()) # type: ignore
        if not response or not response.value:
            values = response.value # type: ignore                             # pulls values from the graph api response
            exists = False
            for child in values:  # type: ignore
                if child.name == child_folder_name:
                    exists = True
            return exists
    

    ##-- Outlook --##

    async def send_email(self, subject_line, email_content, sender, email_address):
        request_body = SendMailPostRequestBody(
        message = Message(
            subject = subject_line,
            body = ItemBody(
                content_type = BodyType.Text,
                content = email_content,
            ),
            to_recipients = [
                Recipient(
                    email_address = EmailAddress(
                        address = email_address,
                    ),
                ),
            ],
        ),
        
        save_to_sent_items = False,
)
        await self.graph_client.users.by_user_id(sender).send_mail.post(request_body)


    ##-- Users --##

    async def get_all_users(self): 
        all_users = await self.graph_client.users.get()
        users = all_users.value # type: ignore
        users_object = []
        for user in users: # type: ignore
            user_info = [user.given_name, user.surname, user.mail]
            if all (user_info):
                users_object.append(user_info)
        #print, for debugging
        #for user in users_object:
        #    print(user)
        ##
        return users_object 


 
    

# Testing
import asyncio
TARGET_FOLDER_ID = "01CYM3L6U7MVDREKPVTFFIZ67RMFTINHCU" #zzz - Project Folder Template
NEW_LOCATION_ID = "01CYM3L6TXOA256KAH4ZFLRHLVPZQ4HNJD"  #1- Current Projects
NEW_FOLDER_NAME = "new folder totally not made by an AI" 
DELETE_TARGET = "01CYM3L6RBPRCU7PKD3NB3I5SOSD5CKFJB" 
MOVE_TARGET = "01CYM3L6TXAGDYIHXE6JB3X3OFNINP7UAO" 
GET_ID = ""    
PARENT_FOLDER_ID = "01CYM3L6R4XVE2WZ47YVE275YCAFITZX4Q"  #Clients
CHILD_FOLDER_NAME = "ZZZ - New Client Template"  
JN = "JN6444"
CLIENT_TEMPLATE_FOLDER_ID = "01CYM3L6TYUPRU5TZANZDII2Y3IO6MLBGY"



if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()       # load secure keys to environment
    graph = GraphAPI() # type: ignore
    #asyncio.run(graph.copy_folder(TARGET_FOLDER_ID, NEW_LOCATION_ID, NEW_FOLDER_NAME))     # copy folder to new location and rename
    #asyncio.run(graph.create_folder(NEW_LOCATION_ID, NEW_FOLDER_NAME))                     # create new folder
    #asyncio.run(graph.delete_item(DELETE_TARGET))                                          # delete item
    #asyncio.run(graph.move_item(MOVE_TARGET, NEW_LOCATION_ID))                             # move item
    #print(asyncio.run(graph.get_folder_id_by_name(PARENT_FOLDER_ID, "TEST CLIENT")))       # get folder id from name and location
    asyncio.run(graph.list_folders(PARENT_FOLDER_ID))                                       # lists folder in parent
    #print(asyncio.run(graph.folder_exists(PARENT_FOLDER_ID, "TEST CLIENT")))               # checks if a folder exists and returns bool
    #print(asyncio.run(graph.get_folder_id_by_partial_name(NEW_LOCATION_ID, JN)))           # get folder id from JN (AroFlo Job Number) and location
    sub = "Test one two"
    cont = "this is not a drill, or is it?"
    fr = "support@focusav.com.au"
    to = "amitchell@focusav.com.au"
    #asyncio.run(graph.send_email(sub, cont, fr, to))
    #asyncio.run(graph.get_all_users())

    
#'''
