from unittest.mock import AsyncMock, MagicMock
import pytest

from src.python_msgraph_toolkit.services.sharepoint.files import FileService
from src.python_msgraph_toolkit.services.sharepoint.drives import DriveService
from src.python_msgraph_toolkit.services.sharepoint.sites import SitesService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError

@pytest.fixture
def initialise_mock():
    return MagicMock()

# to test sharepoint run from root directory: 
# pytest tests/unit/test_sharepoint.py

# to test all run from root directory: 
# pytest tests/unit

@pytest.mark.asyncio
async def test_list_folder_contents(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_response = MagicMock(value=[])
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.children.get = AsyncMock(
        return_value=mock_response
    )

    drive_id = "mock_drive_id"
    parent_folder_id = "mock_parent_folder_id"

    await service.list_folder_contents(drive_id=drive_id, parent_folder_id=parent_folder_id)

    mock_client.drives.by_drive_id.assert_called_once_with(drive_id)
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.assert_called_once_with(parent_folder_id)


@pytest.mark.asyncio
async def test_list_folder_contents_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.list_folder_contents(parent_folder_id="folder1")


@pytest.mark.asyncio
async def test_list_folder_contents_missing_parent_folder_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Parent folder ID is required"):
        await service.list_folder_contents(drive_id="drive1")


@pytest.mark.asyncio
async def test_list_folder_contents_api_error(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.children.get = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.list_folder_contents(drive_id="d1", parent_folder_id="f1")


# ─── FileService: get_item_by_name ───

@pytest.mark.asyncio
async def test_get_item_by_name(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_item = MagicMock(name="found_item")
    mock_response = MagicMock(value=[mock_item])
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.children.get = AsyncMock(
        return_value=mock_response
    )

    result = await service.get_item_by_name(drive_id="d1", parent_folder_id="f1", item_name="report.pdf")

    assert result is mock_item
    mock_client.drives.by_drive_id.assert_called_once_with("d1")
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.assert_called_once_with("f1")


@pytest.mark.asyncio
async def test_get_item_by_name_not_found(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_response = MagicMock(value=[])
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.children.get = AsyncMock(
        return_value=mock_response
    )

    result = await service.get_item_by_name(drive_id="d1", parent_folder_id="f1", item_name="missing.pdf")
    assert result is None


@pytest.mark.asyncio
async def test_get_item_by_name_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.get_item_by_name(parent_folder_id="f1", item_name="test.txt")


@pytest.mark.asyncio
async def test_get_item_by_name_missing_item_name(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Item name is required"):
        await service.get_item_by_name(drive_id="d1", parent_folder_id="f1")


# ─── FileService: get_item_by_path ───

@pytest.mark.asyncio
async def test_get_item_by_path(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_item = MagicMock(name="path_item")
    mock_client.drives.by_drive_id.return_value.root.with_url.return_value.get = AsyncMock(
        return_value=mock_item
    )

    result = await service.get_item_by_path(drive_id="d1", item_path="/docs/report.pdf")

    assert result is mock_item
    mock_client.drives.by_drive_id.assert_called_once_with("d1")


@pytest.mark.asyncio
async def test_get_item_by_path_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.get_item_by_path(item_path="/docs/file.txt")


@pytest.mark.asyncio
async def test_get_item_by_path_missing_item_path(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Item path is required"):
        await service.get_item_by_path(drive_id="d1")


# ─── FileService: get_item_by_id ───

@pytest.mark.asyncio
async def test_get_item_by_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_item = MagicMock(name="id_item")
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.get = AsyncMock(
        return_value=mock_item
    )

    result = await service.get_item_by_id(drive_id="d1", item_id="item123")

    assert result is mock_item
    mock_client.drives.by_drive_id.assert_called_once_with("d1")
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.assert_called_once_with("item123")


@pytest.mark.asyncio
async def test_get_item_by_id_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.get_item_by_id(item_id="item1")


@pytest.mark.asyncio
async def test_get_item_by_id_missing_item_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Item ID is required"):
        await service.get_item_by_id(drive_id="d1")


# ─── FileService: create_folder ───

@pytest.mark.asyncio
async def test_create_folder(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_folder = MagicMock(name="created_folder")
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.children.post = AsyncMock(
        return_value=mock_folder
    )

    result = await service.create_folder(drive_id="d1", parent_folder_id="f1", new_folder_name="Reports")

    assert result is mock_folder
    mock_client.drives.by_drive_id.assert_called_once_with("d1")
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.assert_called_once_with("f1")


@pytest.mark.asyncio
async def test_create_folder_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.create_folder(parent_folder_id="f1", new_folder_name="New")


@pytest.mark.asyncio
async def test_create_folder_missing_folder_name(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="New folder name is required"):
        await service.create_folder(drive_id="d1", parent_folder_id="f1")


# ─── FileService: delete_item ───

@pytest.mark.asyncio
async def test_delete_item(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.delete = AsyncMock()

    await service.delete_item(drive_id="d1", item_id="item1")

    mock_client.drives.by_drive_id.assert_called_once_with("d1")
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.assert_called_once_with("item1")


@pytest.mark.asyncio
async def test_delete_item_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.delete_item(item_id="item1")


@pytest.mark.asyncio
async def test_delete_item_missing_item_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Item ID is required"):
        await service.delete_item(drive_id="d1")


# ─── FileService: move_item ───

@pytest.mark.asyncio
async def test_move_item(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.return_value.patch = AsyncMock()

    await service.move_item(drive_id="d1", item_id="item1", new_location_id="loc2")

    mock_client.drives.by_drive_id.assert_called_once_with("d1")
    mock_client.drives.by_drive_id.return_value.items.by_drive_item_id.assert_called_once_with("item1")


@pytest.mark.asyncio
async def test_move_item_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.move_item(item_id="item1", new_location_id="loc1")


@pytest.mark.asyncio
async def test_move_item_missing_new_location(initialise_mock):
    mock_client = initialise_mock
    service = FileService(mock_client)

    with pytest.raises(ValidationError, match="New location ID is required"):
        await service.move_item(drive_id="d1", item_id="item1")


# ─── DriveService: get_drive_root_folder ───

@pytest.mark.asyncio
async def test_get_drive_root_folder(initialise_mock):
    mock_client = initialise_mock
    service = DriveService(mock_client)

    mock_root = MagicMock(name="root_folder")
    mock_client.drives.by_drive_id.return_value.root.get = AsyncMock(return_value=mock_root)

    result = await service.get_drive_root_folder(drive_id="drive123")

    assert result is mock_root
    mock_client.drives.by_drive_id.assert_called_once_with("drive123")


@pytest.mark.asyncio
async def test_get_drive_root_folder_missing_drive_id(initialise_mock):
    mock_client = initialise_mock
    service = DriveService(mock_client)

    with pytest.raises(ValidationError, match="Drive ID is required"):
        await service.get_drive_root_folder()


@pytest.mark.asyncio
async def test_get_drive_root_folder_api_error(initialise_mock):
    mock_client = initialise_mock
    service = DriveService(mock_client)

    mock_client.drives.by_drive_id.return_value.root.get = AsyncMock(
        side_effect=Exception("not found 404")
    )

    with pytest.raises(GraphAPIError):
        await service.get_drive_root_folder(drive_id="bad_drive")


# ─── SitesService: get_all_sites ───

@pytest.mark.asyncio
async def test_get_all_sites(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    mock_sites = [MagicMock(display_name="Site A"), MagicMock(display_name="Site B")]
    mock_response = MagicMock(value=mock_sites)
    mock_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

    result = await service.get_all_sites()

    assert result == mock_sites


@pytest.mark.asyncio
async def test_get_all_sites_empty(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    mock_response = MagicMock(value=None)
    mock_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

    result = await service.get_all_sites()
    assert result == []


@pytest.mark.asyncio
async def test_get_all_sites_api_error(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    mock_client.sites.get_all_sites.get = AsyncMock(side_effect=Exception("server error"))

    with pytest.raises(GraphAPIError):
        await service.get_all_sites()


# ─── SitesService: get_site_by_id ───

@pytest.mark.asyncio
async def test_get_site_by_id(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    mock_site = MagicMock(display_name="My Site")
    mock_client.sites.by_site_id.return_value.get = AsyncMock(return_value=mock_site)

    result = await service.get_site_by_id(site_id="site123")

    assert result is mock_site
    mock_client.sites.by_site_id.assert_called_once_with("site123")


@pytest.mark.asyncio
async def test_get_site_by_id_missing(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    with pytest.raises(ValidationError, match="Site ID is required"):
        await service.get_site_by_id()


# ─── SitesService: get_site_by_displayname ───

@pytest.mark.asyncio
async def test_get_site_by_displayname_found(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    site_a = MagicMock(display_name="Project Alpha")
    site_b = MagicMock(display_name="Project Beta")
    mock_response = MagicMock(value=[site_a, site_b])
    mock_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

    result = await service.get_site_by_displayname(site_name="Project Alpha")
    assert result is site_a


@pytest.mark.asyncio
async def test_get_site_by_displayname_case_insensitive(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    site = MagicMock(display_name="My Site")
    mock_response = MagicMock(value=[site])
    mock_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

    result = await service.get_site_by_displayname(site_name="my site")
    assert result is site


@pytest.mark.asyncio
async def test_get_site_by_displayname_not_found(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    site = MagicMock(display_name="Other Site")
    mock_response = MagicMock(value=[site])
    mock_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

    result = await service.get_site_by_displayname(site_name="NonExistent")
    assert result is None


@pytest.mark.asyncio
async def test_get_site_by_displayname_missing_name(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    with pytest.raises(ValidationError, match="Site Name is required"):
        await service.get_site_by_displayname()


# ─── SitesService: get_sub_sites ───

@pytest.mark.asyncio
async def test_get_sub_sites(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    subsites = [MagicMock(display_name="Sub1"), MagicMock(display_name="Sub2")]
    mock_response = MagicMock(value=subsites)
    mock_client.sites.by_site_id.return_value.sites.get = AsyncMock(return_value=mock_response)

    result = await service.get_sub_sites(parent_site_id="parent123")

    assert result == subsites
    mock_client.sites.by_site_id.assert_called_once_with("parent123")


@pytest.mark.asyncio
async def test_get_sub_sites_empty(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    mock_response = MagicMock(value=None)
    mock_client.sites.by_site_id.return_value.sites.get = AsyncMock(return_value=mock_response)

    result = await service.get_sub_sites(parent_site_id="parent123")
    assert result == []


@pytest.mark.asyncio
async def test_get_sub_sites_missing_id(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    with pytest.raises(ValidationError, match="Parent site ID is required"):
        await service.get_sub_sites()


# ─── SitesService: get_site_drive ───

@pytest.mark.asyncio
async def test_get_site_drive(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    mock_drive = MagicMock(name="site_drive")
    mock_client.sites.by_site_id.return_value.drive.get = AsyncMock(return_value=mock_drive)

    result = await service.get_site_drive(site_id="site123")

    assert result is mock_drive
    mock_client.sites.by_site_id.assert_called_once_with("site123")


@pytest.mark.asyncio
async def test_get_site_drive_missing_id(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    with pytest.raises(ValidationError, match="Site ID is required"):
        await service.get_site_drive()


@pytest.mark.asyncio
async def test_get_site_drive_not_found(initialise_mock):
    mock_client = initialise_mock
    service = SitesService(mock_client)

    mock_client.sites.by_site_id.return_value.drive.get = AsyncMock(return_value=None)

    result = await service.get_site_drive(site_id="site123")
    assert result is None