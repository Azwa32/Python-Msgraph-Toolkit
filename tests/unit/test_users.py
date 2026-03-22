from unittest.mock import AsyncMock, MagicMock
import pytest

from src.python_msgraph_toolkit.services.users.users import UserService
from src.python_msgraph_toolkit.services.exceptions import ValidationError, GraphAPIError

@pytest.fixture
def initialise_mock():
    return MagicMock()

# to test from root directory: 
# pytest tests/unit/test_users.py

# to test all run from root directory: 
# pytest tests/unit

@pytest.mark.asyncio
async def test_get_user(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_user = MagicMock()
    mock_client.users.by_user_id.return_value.get = AsyncMock(return_value=mock_user)

    result = await service.get_user(user_id="user1")

    assert result is mock_user
    mock_client.users.by_user_id.assert_called_once_with("user1")


@pytest.mark.asyncio
async def test_get_user_not_found(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_client.users.by_user_id.return_value.get = AsyncMock(return_value=None)

    result = await service.get_user(user_id="user1")
    assert result is None


@pytest.mark.asyncio
async def test_get_user_missing_user_id(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    with pytest.raises(ValidationError, match="user_id is required"):
        await service.get_user()


@pytest.mark.asyncio
async def test_get_user_api_error(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_client.users.by_user_id.return_value.get = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.get_user(user_id="user1")


# ─── UserService: list_users ───

@pytest.mark.asyncio
async def test_list_users(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_users = [MagicMock(), MagicMock()]
    mock_response = MagicMock(value=mock_users)
    mock_client.users.get = AsyncMock(return_value=mock_response)

    result = await service.list_users()

    assert result == mock_users


@pytest.mark.asyncio
async def test_list_users_empty(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_response = MagicMock(value=None)
    mock_client.users.get = AsyncMock(return_value=mock_response)

    result = await service.list_users()
    assert result is None


@pytest.mark.asyncio
async def test_list_users_no_response(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_client.users.get = AsyncMock(return_value=None)

    result = await service.list_users()
    assert result is None


@pytest.mark.asyncio
async def test_list_users_api_error(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_client.users.get = AsyncMock(side_effect=Exception("server error"))

    with pytest.raises(GraphAPIError):
        await service.list_users()


# ─── UserService: get_user_by_email ───

@pytest.mark.asyncio
async def test_get_user_by_email(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_user = MagicMock()
    mock_client.users.by_user_id.return_value.get = AsyncMock(return_value=mock_user)

    result = await service.get_user_by_email(email="test@example.com")

    assert result is mock_user
    mock_client.users.by_user_id.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_client.users.by_user_id.return_value.get = AsyncMock(return_value=None)

    result = await service.get_user_by_email(email="test@example.com")
    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email_missing_email(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    with pytest.raises(ValidationError, match="email is required"):
        await service.get_user_by_email()


@pytest.mark.asyncio
async def test_get_user_by_email_api_error(initialise_mock):
    mock_client = initialise_mock
    service = UserService(mock_client)

    mock_client.users.by_user_id.return_value.get = AsyncMock(
        side_effect=Exception("server error")
    )

    with pytest.raises(GraphAPIError):
        await service.get_user_by_email(email="test@example.com")
