import pytest
from unittest.mock import AsyncMock, MagicMock

from src.python_msgraph_toolkit.services.users.users import UserService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError


class TestUserServiceInit:
    def test_init_with_valid_client(self, mock_graph_client):
        service = UserService(mock_graph_client)
        assert service._msgraph_client is mock_graph_client

    def test_init_with_none_client_raises(self):
        with pytest.raises(ValidationError, match="msgraph client must be supplied"):
            UserService(None)


class TestGetUser:
    @pytest.fixture
    def user_service(self, mock_graph_client):
        return UserService(mock_graph_client)

    async def test_missing_user_id_raises(self, user_service):
        with pytest.raises(ValidationError, match="user_id is required"):
            await user_service.get_user()

    async def test_successful_get(self, user_service, mock_graph_client):
        mock_user = MagicMock(display_name="John Doe")
        mock_graph_client.users.by_user_id.return_value.get = AsyncMock(return_value=mock_user)

        result = await user_service.get_user(user_id="user123")
        assert result is mock_user
        mock_graph_client.users.by_user_id.assert_called_with("user123")

    async def test_user_not_found_returns_none(self, user_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.get = AsyncMock(return_value=None)

        result = await user_service.get_user(user_id="unknown")
        assert result is None

    async def test_api_error_raises(self, user_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.get = AsyncMock(
            side_effect=Exception("not found 404")
        )
        with pytest.raises(GraphAPIError):
            await user_service.get_user(user_id="bad_user")


class TestListUsers:
    @pytest.fixture
    def user_service(self, mock_graph_client):
        return UserService(mock_graph_client)

    async def test_successful_list(self, user_service, mock_graph_client):
        users = [MagicMock(display_name="Alice"), MagicMock(display_name="Bob")]
        mock_response = MagicMock(value=users)
        mock_graph_client.users.get = AsyncMock(return_value=mock_response)

        result = await user_service.list_users()
        assert result == users

    async def test_empty_list_returns_none(self, user_service, mock_graph_client):
        mock_response = MagicMock(value=None)
        mock_graph_client.users.get = AsyncMock(return_value=mock_response)

        result = await user_service.list_users()
        assert result is None

    async def test_none_response_returns_none(self, user_service, mock_graph_client):
        mock_graph_client.users.get = AsyncMock(return_value=None)

        result = await user_service.list_users()
        assert result is None

    async def test_api_error_raises(self, user_service, mock_graph_client):
        mock_graph_client.users.get = AsyncMock(side_effect=Exception("server error"))

        with pytest.raises(GraphAPIError):
            await user_service.list_users()


class TestGetUserByEmail:
    @pytest.fixture
    def user_service(self, mock_graph_client):
        return UserService(mock_graph_client)

    async def test_missing_email_raises(self, user_service):
        with pytest.raises(ValidationError, match="email is required"):
            await user_service.get_user_by_email()

    async def test_successful_get(self, user_service, mock_graph_client):
        mock_user = MagicMock(mail="alice@test.com")
        mock_graph_client.users.by_user_id.return_value.get = AsyncMock(return_value=mock_user)

        result = await user_service.get_user_by_email(email="alice@test.com")
        assert result is mock_user

    async def test_user_not_found_returns_none(self, user_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.get = AsyncMock(return_value=None)

        result = await user_service.get_user_by_email(email="missing@test.com")
        assert result is None

    async def test_api_error_raises(self, user_service, mock_graph_client):
        mock_graph_client.users.by_user_id.return_value.get = AsyncMock(
            side_effect=Exception("access denied 403")
        )
        with pytest.raises(GraphAPIError):
            await user_service.get_user_by_email(email="forbidden@test.com")
