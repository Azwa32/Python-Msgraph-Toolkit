import pytest
from unittest.mock import AsyncMock, MagicMock

from src.python_msgraph_toolkit.services.sharepoint.files import FileService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError


class TestFileServiceInit:
    def test_init_with_valid_client(self, mock_graph_client):
        service = FileService(mock_graph_client)
        assert service._msgraph_client is mock_graph_client

    def test_init_with_none_client_raises(self):
        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            FileService(None)


class TestListFolderContents:
    @pytest.fixture
    def file_service(self, mock_graph_client):
        return FileService(mock_graph_client)

    async def test_missing_drive_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await file_service.list_folder_contents(parent_folder_id="folder1")

    async def test_missing_parent_folder_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Parent folder ID is required"):
            await file_service.list_folder_contents(drive_id="drive1")

    async def test_successful_list(self, file_service, mock_graph_client):
        items = [MagicMock(name="item1"), MagicMock(name="item2")]
        mock_response = MagicMock(value=items)
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .children.get = AsyncMock(return_value=mock_response)

        result = await file_service.list_folder_contents(drive_id="d1", parent_folder_id="f1")

        assert result == items
        mock_graph_client.drives.by_drive_id.assert_called_with("d1")

    async def test_empty_response_returns_empty_list(self, file_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .children.get = AsyncMock(return_value=mock_response)

        result = await file_service.list_folder_contents(drive_id="d1", parent_folder_id="f1")
        assert result == []

    async def test_api_error_raises(self, file_service, mock_graph_client):
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .children.get = AsyncMock(side_effect=Exception("server error"))

        with pytest.raises(GraphAPIError):
            await file_service.list_folder_contents(drive_id="d1", parent_folder_id="f1")


class TestGetItemByName:
    @pytest.fixture
    def file_service(self, mock_graph_client):
        return FileService(mock_graph_client)

    async def test_missing_drive_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await file_service.get_item_by_name(parent_folder_id="f1", item_name="test.txt")

    async def test_missing_parent_folder_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Parent folder ID is required"):
            await file_service.get_item_by_name(drive_id="d1", item_name="test.txt")

    async def test_missing_item_name_raises(self, file_service):
        with pytest.raises(ValidationError, match="Item name is required"):
            await file_service.get_item_by_name(drive_id="d1", parent_folder_id="f1")

    async def test_item_found(self, file_service, mock_graph_client):
        mock_item = MagicMock(name="found_item")
        mock_response = MagicMock(value=[mock_item])
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .children.get = AsyncMock(return_value=mock_response)

        result = await file_service.get_item_by_name(drive_id="d1", parent_folder_id="f1", item_name="report.pdf")
        assert result is mock_item

    async def test_item_not_found_returns_none(self, file_service, mock_graph_client):
        mock_response = MagicMock(value=[])
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .children.get = AsyncMock(return_value=mock_response)

        result = await file_service.get_item_by_name(drive_id="d1", parent_folder_id="f1", item_name="missing.pdf")
        assert result is None


class TestGetItemByPath:
    @pytest.fixture
    def file_service(self, mock_graph_client):
        return FileService(mock_graph_client)

    async def test_missing_drive_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await file_service.get_item_by_path(item_path="/docs/file.txt")

    async def test_missing_item_path_raises(self, file_service):
        with pytest.raises(ValidationError, match="Item path is required"):
            await file_service.get_item_by_path(drive_id="d1")

    async def test_successful_get(self, file_service, mock_graph_client):
        mock_item = MagicMock(name="path_item")
        mock_graph_client.drives.by_drive_id.return_value \
            .root.with_url.return_value \
            .get = AsyncMock(return_value=mock_item)

        result = await file_service.get_item_by_path(drive_id="d1", item_path="/docs/report.pdf")
        assert result is mock_item


class TestGetItemById:
    @pytest.fixture
    def file_service(self, mock_graph_client):
        return FileService(mock_graph_client)

    async def test_missing_drive_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await file_service.get_item_by_id(item_id="item1")

    async def test_missing_item_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Item ID is required"):
            await file_service.get_item_by_id(drive_id="d1")

    async def test_successful_get(self, file_service, mock_graph_client):
        mock_item = MagicMock(name="id_item")
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .get = AsyncMock(return_value=mock_item)

        result = await file_service.get_item_by_id(drive_id="d1", item_id="item123")
        assert result is mock_item


class TestCreateFolder:
    @pytest.fixture
    def file_service(self, mock_graph_client):
        return FileService(mock_graph_client)

    async def test_missing_drive_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await file_service.create_folder(parent_folder_id="f1", new_folder_name="New")

    async def test_missing_parent_folder_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Parent folder ID is required"):
            await file_service.create_folder(drive_id="d1", new_folder_name="New")

    async def test_missing_folder_name_raises(self, file_service):
        with pytest.raises(ValidationError, match="New folder name is required"):
            await file_service.create_folder(drive_id="d1", parent_folder_id="f1")

    async def test_successful_create(self, file_service, mock_graph_client):
        mock_folder = MagicMock(name="created_folder")
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .children.post = AsyncMock(return_value=mock_folder)

        result = await file_service.create_folder(drive_id="d1", parent_folder_id="f1", new_folder_name="Reports")
        assert result is mock_folder


class TestDeleteItem:
    @pytest.fixture
    def file_service(self, mock_graph_client):
        return FileService(mock_graph_client)

    async def test_missing_drive_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await file_service.delete_item(item_id="item1")

    async def test_missing_item_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Item ID is required"):
            await file_service.delete_item(drive_id="d1")

    async def test_successful_delete(self, file_service, mock_graph_client):
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .delete = AsyncMock()

        await file_service.delete_item(drive_id="d1", item_id="item1")
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .delete.assert_awaited_once()


class TestMoveItem:
    @pytest.fixture
    def file_service(self, mock_graph_client):
        return FileService(mock_graph_client)

    async def test_missing_drive_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await file_service.move_item(item_id="item1", new_location_id="loc1")

    async def test_missing_item_id_raises(self, file_service):
        with pytest.raises(ValidationError, match="Item ID is required"):
            await file_service.move_item(drive_id="d1", new_location_id="loc1")

    async def test_missing_new_location_raises(self, file_service):
        with pytest.raises(ValidationError, match="New location ID is required"):
            await file_service.move_item(drive_id="d1", item_id="item1")

    async def test_successful_move(self, file_service, mock_graph_client):
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .patch = AsyncMock()

        await file_service.move_item(drive_id="d1", item_id="item1", new_location_id="loc2")
        mock_graph_client.drives.by_drive_id.return_value \
            .items.by_drive_item_id.return_value \
            .patch.assert_awaited_once()
