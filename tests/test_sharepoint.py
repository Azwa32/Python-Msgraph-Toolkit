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
from src.python_msgraph_toolkit.client import GraphClient

# to run tests from root folder: pytest test_sharepoint.py -W ignore::DeprecationWarning
# to run a single test from root folder (with print -s) eg: 
# pytest tests/test_sharepoint.py::test_sites_getsites -s -W ignore::DeprecationWarning

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
async def test_sites_get_sites(initialize_client):
    client = initialize_client
    sites = await client.sharepoint.sites.get_all_sites()
    if sites:
        print("\n")
        for site in sites:
            print(site.display_name)
    assert sites is not None

@pytest.mark.asyncio
async def test_sites_get_site_by_displayname(initialize_client):
    sites_name = str(os.getenv("TEST_SHAREPOINT_SITE_NAME"))
    client = initialize_client
    site = await client.sharepoint.sites.get_site_by_displayname(site_name=sites_name)
    if site:
        print(f"\nSite Name: {site.display_name}, Site ID: {site.id}")
    assert site is not None
    assert site.display_name == sites_name 

@pytest.mark.asyncio  
async def test_sites_get_site_drive(initialize_client):
    sites_id = str(os.getenv("TEST_SHAREPOINT_SITE_ID"))
    client = initialize_client
    drive = await client.sharepoint.sites.get_site_drive(site_id=sites_id)
    if drive:
        print(f"\nDrive ID: {drive.id}")
    assert drive is not None
    assert type(drive.id) == str
    assert len(drive.id) > 10

@pytest.mark.asyncio
async def test_drives_get_drive_root_folder(initialize_client):
    test_drive_id = str(os.getenv("TEST_SHAREPOINT_DRIVE_ID"))
    client = initialize_client
    root_folder = await client.sharepoint.drives.get_drive_root_folder(drive_id=test_drive_id)
    if root_folder:
        print(f"\nRoot Folder Name: {root_folder.name}, Root Folder ID: {root_folder.id}")
    assert root_folder is not None
    assert len(root_folder.id) > 10

@pytest.mark.asyncio
async def test_files_list_folder_contents(initialize_client):
    test_drive_id = str(os.getenv("TEST_SHAREPOINT_DRIVE_ID"))
    test_parent_folder_id = str(os.getenv("TEST_SHAREPOINT_PARENT_FOLDER_ID"))
    client = initialize_client
    result = await client.sharepoint.files.list_folder_contents(drive_id=test_drive_id, parent_folder_id=test_parent_folder_id)
    if result:
        print("\n")
        for file in result:
            print(file.name)
    assert isinstance(result, list)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_files_get_item_by_name(initialize_client):
    test_drive_id = str(os.getenv("TEST_SHAREPOINT_DRIVE_ID"))
    test_parent_folder_id = str(os.getenv("TEST_SHAREPOINT_PARENT_FOLDER_ID"))
    test_item_name = str(os.getenv("TEST_SHAREPOINT_ITEM_NAME"))
    client = initialize_client
    item = await client.sharepoint.files.get_item_by_name(drive_id=test_drive_id, parent_folder_id=test_parent_folder_id, item_name=test_item_name)
    if item:
        print("\n")
        print(f"Item Name: {item.name}, Item Path: {item.web_url}")
    assert item is not None
    assert len(item.name) > 0       

@pytest.mark.asyncio
async def test_files_get_item_by_path(initialize_client):
    test_drive_id = str(os.getenv("TEST_SHAREPOINT_DRIVE_ID"))
    test_item_path = str(os.getenv("TEST_SHAREPOINT_ITEM_PATH"))
    client = initialize_client
    item = await client.sharepoint.files.get_item_by_path(drive_id=test_drive_id, item_path=test_item_path)
    if item:
        print("\n")
        print(f"Item Name: {item.name}, Item ID: {item.id}")
    assert item is not None
    assert len(item.name) > 0   

@pytest.mark.asyncio
async def test_files_get_item_by_id(initialize_client):
    test_drive_id = str(os.getenv("TEST_SHAREPOINT_DRIVE_ID"))
    test_item_id = str(os.getenv("TEST_SHAREPOINT_ITEM_ID"))
    client = initialize_client
    item = await client.sharepoint.files.get_item_by_id(drive_id=test_drive_id, item_id=test_item_id)
    if item:
        print(f"Item: {item.name}")
    assert item is not None
    assert len(item.name) > 0   