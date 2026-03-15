from src.msgraph_api.client import GraphClient
from dotenv import load_dotenv
import os

load_dotenv()
client = GraphClient(
    str(os.getenv("MSGRAPH_TENANT_ID")),
    str(os.getenv("MSGRAPH_CLIENT_ID")),
    str(os.getenv("MSGRAPH_API_KEY"))
    )
print(f'MSGraph Client is: {client.authorised and "Initialised"or "Not Initialised"}')


