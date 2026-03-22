import pytest
from unittest.mock import AsyncMock, MagicMock

from src.python_msgraph_toolkit.services.sharepoint.drives import DriveService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError


class TestDriveServiceInit:
    def test_init_with_valid_client(self, mock_graph_client):
        service = DriveService(mock_graph_client)
        assert service._msgraph_client is mock_graph_client

    def test_init_with_none_client_raises(self):
        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            DriveService(None)


class TestGetDriveRootFolder:
    @pytest.fixture
    def drive_service(self, mock_graph_client):
        return DriveService(mock_graph_client)

    async def test_missing_drive_id_raises(self, drive_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await drive_service.get_drive_root_folder()

    async def test_empty_drive_id_raises(self, drive_service):
        with pytest.raises(ValidationError, match="Drive ID is required"):
            await drive_service.get_drive_root_folder(drive_id="")

    async def test_successful_get(self, drive_service, mock_graph_client):
        mock_root = MagicMock(name="root_folder")
        mock_graph_client.drives.by_drive_id.return_value.root.get = AsyncMock(return_value=mock_root)

        result = await drive_service.get_drive_root_folder(drive_id="drive123")

        mock_graph_client.drives.by_drive_id.assert_called_once_with("drive123")
        assert result is mock_root

    async def test_api_error_raises_graph_error(self, drive_service, mock_graph_client):
        mock_graph_client.drives.by_drive_id.return_value.root.get = AsyncMock(
            side_effect=Exception("not found 404")
        )

        with pytest.raises(GraphAPIError):
            await drive_service.get_drive_root_folder(drive_id="bad_drive")
