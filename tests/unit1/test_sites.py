import pytest
from unittest.mock import AsyncMock, MagicMock

from src.python_msgraph_toolkit.services.sharepoint.sites import SitesService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError


class TestSitesServiceInit:
    def test_init_with_valid_client(self, mock_graph_client):
        service = SitesService(mock_graph_client)
        assert service._msgraph_client is mock_graph_client

    def test_init_with_none_client_raises(self):
        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            SitesService(None)


class TestGetAllSites:
    @pytest.fixture
    def sites_service(self, mock_graph_client):
        return SitesService(mock_graph_client)

    async def test_successful_get_all(self, sites_service, mock_graph_client):
        mock_sites = [MagicMock(display_name="Site A"), MagicMock(display_name="Site B")]
        mock_response = MagicMock(value=mock_sites)
        mock_graph_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_all_sites()
        assert result == mock_sites

    async def test_empty_response_returns_empty_list(self, sites_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_all_sites()
        assert result == []

    async def test_api_error_raises(self, sites_service, mock_graph_client):
        mock_graph_client.sites.get_all_sites.get = AsyncMock(side_effect=Exception("server error"))

        with pytest.raises(GraphAPIError):
            await sites_service.get_all_sites()


class TestGetSiteById:
    @pytest.fixture
    def sites_service(self, mock_graph_client):
        return SitesService(mock_graph_client)

    async def test_missing_site_id_raises(self, sites_service):
        with pytest.raises(ValidationError, match="Site ID is required"):
            await sites_service.get_site_by_id()

    async def test_successful_get(self, sites_service, mock_graph_client):
        mock_site = MagicMock(display_name="My Site")
        mock_graph_client.sites.by_site_id.return_value.get = AsyncMock(return_value=mock_site)

        result = await sites_service.get_site_by_id(site_id="site123")
        assert result is mock_site
        mock_graph_client.sites.by_site_id.assert_called_with("site123")

    async def test_none_response_returns_none(self, sites_service, mock_graph_client):
        mock_graph_client.sites.by_site_id.return_value.get = AsyncMock(return_value=None)

        result = await sites_service.get_site_by_id(site_id="site123")
        assert result is None


class TestGetSiteByDisplayname:
    @pytest.fixture
    def sites_service(self, mock_graph_client):
        return SitesService(mock_graph_client)

    async def test_missing_site_name_raises(self, sites_service):
        with pytest.raises(ValidationError, match="Site Name is required"):
            await sites_service.get_site_by_displayname()

    async def test_matching_site_found(self, sites_service, mock_graph_client):
        site_a = MagicMock(display_name="Project Alpha")
        site_b = MagicMock(display_name="Project Beta")
        mock_response = MagicMock(value=[site_a, site_b])
        mock_graph_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_site_by_displayname(site_name="Project Alpha")
        assert result is site_a

    async def test_case_insensitive_match(self, sites_service, mock_graph_client):
        site = MagicMock(display_name="My Site")
        mock_response = MagicMock(value=[site])
        mock_graph_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_site_by_displayname(site_name="my site")
        assert result is site

    async def test_no_match_returns_none(self, sites_service, mock_graph_client):
        site = MagicMock(display_name="Other Site")
        mock_response = MagicMock(value=[site])
        mock_graph_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_site_by_displayname(site_name="NonExistent")
        assert result is None

    async def test_empty_sites_returns_none(self, sites_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.sites.get_all_sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_site_by_displayname(site_name="Any")
        assert result is None


class TestGetSubSites:
    @pytest.fixture
    def sites_service(self, mock_graph_client):
        return SitesService(mock_graph_client)

    async def test_missing_parent_site_id_raises(self, sites_service):
        with pytest.raises(ValidationError, match="Parent site ID is required"):
            await sites_service.get_sub_sites()

    async def test_successful_get_subsites(self, sites_service, mock_graph_client):
        subsites = [MagicMock(display_name="Sub1"), MagicMock(display_name="Sub2")]
        mock_response = MagicMock(value=subsites)
        mock_graph_client.sites.by_site_id.return_value.sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_sub_sites(parent_site_id="parent123")
        assert result == subsites

    async def test_no_subsites_returns_empty_list(self, sites_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.sites.by_site_id.return_value.sites.get = AsyncMock(return_value=mock_response)

        result = await sites_service.get_sub_sites(parent_site_id="parent123")
        assert result == []


class TestGetSiteDrive:
    @pytest.fixture
    def sites_service(self, mock_graph_client):
        return SitesService(mock_graph_client)

    async def test_missing_site_id_raises(self, sites_service):
        with pytest.raises(ValidationError, match="Site ID is required"):
            await sites_service.get_site_drive()

    async def test_successful_get_drive(self, sites_service, mock_graph_client):
        mock_drive = MagicMock(name="site_drive")
        mock_graph_client.sites.by_site_id.return_value.drive.get = AsyncMock(return_value=mock_drive)

        result = await sites_service.get_site_drive(site_id="site123")
        assert result is mock_drive

    async def test_none_response_returns_none(self, sites_service, mock_graph_client):
        mock_graph_client.sites.by_site_id.return_value.drive.get = AsyncMock(return_value=None)

        result = await sites_service.get_site_drive(site_id="site123")
        assert result is None
