import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock


@pytest.fixture
def mock_graph_client():
    """Shared mock of GraphServiceClient for all unit tests."""
    client = MagicMock()
    # Set up common async method chains as needed per test
    return client
