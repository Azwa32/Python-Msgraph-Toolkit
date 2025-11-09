import warnings
from dotenv import load_dotenv
from pathlib import Path
import sys
import os
import pytest

# Add src/ to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Now import after sys.path is configured
from msgraph_api.client import GraphClient

# to run tests: pytest sharepoint.py -W ignore::DeprecationWarning

# placeholders for running tests
test_site_name = "FocusAV"
test_site_id = ""


@pytest.fixture
def initialize_client():
    load_dotenv()
    client = GraphClient(
        str(os.getenv("MSGRAPH_TENANT_ID")),
        str(os.getenv("MSGRAPH_CLIENT_ID")),
        str(os.getenv("MSGRAPH_API_KEY"))
        )
    return client

@pytest.mark.asyncio
async def test_sites_getsite_by_displayname(initialize_client):
    sites_name = "FocusAV"
    client = initialize_client
    site = await client.sharepoint.sites.get_site_by_displayname(site_name=sites_name)
    test_site_id = site.id
    assert site is not None
    assert site.display_name == sites_name 

@pytest.mark.asyncio  
async def test_sites_get_site_drive(initialize_client):
    sites_id = "focusav.sharepoint.com,7d86397d-916d-4a16-80fa-8079c08ab0bd,5171c734-d45a-4ddf-832d-c9a99d024290"
    client = initialize_client
    drive = await client.sharepoint.sites.get_site_drive(site_id=sites_id)
    assert drive is not None
    assert type(drive.id) == str
    assert len(drive.id) > 10

@pytest.mark.asyncio
async def test_drives_get_drive_root_folder(initialize_client):
    test_drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
    client = initialize_client
    root_folder = await client.sharepoint.drives.get_drive_root_folder(drive_id=test_drive_id)
    assert root_folder is not None
    assert len(root_folder.id) > 10

@pytest.mark.asyncio
async def test_files_list_folder_contents(initialize_client):
    test_drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
    test_parent_folder_id = "01CYM3L6TXOA256KAH4ZFLRHLVPZQ4HNJD"
    client = initialize_client
    result = await client.sharepoint.files.list_folder_contents(drive_id=test_drive_id, parent_folder_id=test_parent_folder_id)
    assert isinstance(result, list)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_files_get_item_by_name(initialize_client):
    test_drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
    test_parent_folder_id = "01CYM3L6UNFXI2DU5DZJBYGQRRMAO3RSB2"
    test_item_name = "Everett Smith EQ6 HUB Equipment Register.xlsx"
    client = initialize_client
    item = await client.sharepoint.files.get_item_by_name(drive_id=test_drive_id, parent_folder_id=test_parent_folder_id, item_name=test_item_name)
    assert item is not None
    assert len(item.name) > 0       

@pytest.mark.asyncio
async def test_files_get_item_by_path(initialize_client):
    test_drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
    test_item_path = "Clients/1- Current Projects/ESCO - EQ6 [9TE] - The Hub - Master Folder/Everett Smith EQ6 HUB Equipment Register.xlsx"
    client = initialize_client
    item = await client.sharepoint.files.get_item_by_path(drive_id=test_drive_id, item_path=test_item_path)
    assert item is not None
    assert len(item.name) > 0   

@pytest.mark.asyncio
async def test_files_get_item_by_id(initialize_client):
    test_drive_id = "b!fTmGfW2RFkqA-oB5wIqwvTTHcVFa1N9Ngy3JqZ0CQpBClq8sO9MhTrvf9AaXjBGa"
    test_item_id = "01CYM3L6WTDWTOTVO7LJFIWF7PZKHWK7UF"
    client = initialize_client
    item = await client.sharepoint.files.get_item_by_id(drive_id=test_drive_id, item_id=test_item_id)
    assert item is not None
    assert len(item.name) > 0   