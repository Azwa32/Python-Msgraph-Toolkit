import pytest
from unittest.mock import MagicMock, patch

from src.python_msgraph_toolkit.client import GraphClient


class TestGraphClientInit:
    @patch("src.python_msgraph_toolkit.client.Auth")
    def test_successful_init_sets_services(self, mock_auth_class):
        mock_auth = MagicMock()
        mock_auth.authorised = True
        mock_auth._msgraph_client = MagicMock()
        mock_auth_class.return_value = mock_auth

        client = GraphClient("tenant", "client_id", "secret")

        assert client.authorised is True
        assert hasattr(client, "sharepoint")
        assert hasattr(client, "outlook")
        assert hasattr(client, "teams")
        assert hasattr(client, "users")

    @patch("src.python_msgraph_toolkit.client.Auth")
    def test_failed_auth_sets_authorised_false(self, mock_auth_class):
        mock_auth = MagicMock()
        mock_auth.authorised = False
        mock_auth_class.return_value = mock_auth

        client = GraphClient("tenant", "client_id", "secret")

        assert client.authorised is False
        assert not hasattr(client, "sharepoint")

    @patch("src.python_msgraph_toolkit.client.Auth")
    def test_auth_called_with_correct_params(self, mock_auth_class):
        mock_auth = MagicMock()
        mock_auth.authorised = True
        mock_auth._msgraph_client = MagicMock()
        mock_auth_class.return_value = mock_auth

        GraphClient("my_tenant", "my_client", "my_secret")

        mock_auth_class.assert_called_once_with("my_tenant", "my_client", "my_secret")


class TestServiceAggregatorInit:
    """Test that service aggregators reject None clients."""

    def test_sharepoint_service_rejects_none(self):
        from src.python_msgraph_toolkit.services.sharepoint.sharepoint_service import SharepointService
        from src.python_msgraph_toolkit.services.exceptions import ValidationError

        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            SharepointService(None)

    def test_outlook_service_rejects_none(self):
        from src.python_msgraph_toolkit.services.outlook.outlook_service import OutlookService
        from src.python_msgraph_toolkit.services.exceptions import ValidationError

        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            OutlookService(None)

    def test_teams_service_rejects_none(self):
        from src.python_msgraph_toolkit.services.teams.teams_service import TeamsService
        from src.python_msgraph_toolkit.services.exceptions import ValidationError

        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            TeamsService(None)

    def test_users_service_rejects_none(self):
        from src.python_msgraph_toolkit.services.users.users_service import UsersService
        from src.python_msgraph_toolkit.services.exceptions import ValidationError

        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            UsersService(None)
