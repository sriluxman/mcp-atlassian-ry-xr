"""
Shared fixtures for Requirements Yogi unit tests.

This module provides specialized fixtures for testing Requirements Yogi functionality.
It builds upon the root conftest.py fixtures and integrates with the test utilities
framework to provide efficient, reusable test fixtures.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the root tests directory to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from fixtures.requirement_yogi_mocks import (
    MOCK_REQUIREMENT_RESPONSE,
)

from mcp_atlassian.requirement_yogi.config import RequirementYogiConfig
from mcp_atlassian.requirement_yogi.fetcher import RequirementYogiFetcher

# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def requirement_yogi_config_factory():
    """
    Factory for creating RequirementYogiConfig instances with customizable options.

    Returns:
        Callable: Function that creates RequirementYogiConfig instances

    Example:
        def test_config(requirement_yogi_config_factory):
            config = requirement_yogi_config_factory(spaces_filter="TYS,DEV")
            assert config.spaces_filter == "TYS,DEV"
    """

    def _create_config(**overrides):
        defaults = {
            "confluence_url": "https://confluence.example.com",
            "auth_type": "pat",
            "personal_token": "test_pat_token_12345",
        }
        config_data = {**defaults, **overrides}
        return RequirementYogiConfig(**config_data)

    return _create_config


@pytest.fixture
def mock_ry_config(requirement_yogi_config_factory):
    """
    Create a standard mock RequirementYogiConfig instance.

    Returns:
        RequirementYogiConfig: Standard test configuration
    """
    return requirement_yogi_config_factory()


@pytest.fixture
def mock_ry_config_with_filter(requirement_yogi_config_factory):
    """
    Create a RequirementYogiConfig with spaces filter enabled.

    Returns:
        RequirementYogiConfig: Configuration with spaces filter
    """
    return requirement_yogi_config_factory(spaces_filter="TYS,OCX,DEV")


# ============================================================================
# Client/Fetcher Fixtures
# ============================================================================


@pytest.fixture
def mock_ry_session():
    """
    Create a mock requests.Session for RY client testing.

    Returns:
        MagicMock: Mock session with standard response setup
    """
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"key": "test"}'
    mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE
    mock_response.raise_for_status.return_value = None
    mock_session.request.return_value = mock_response
    return mock_session


@pytest.fixture
def requirement_yogi_client(mock_ry_config, mock_ry_session):
    """
    Create a RequirementYogiFetcher with mocked session.

    This fixture patches the Session to avoid real HTTP calls and provides
    a fully functional fetcher for testing mixin methods.

    Args:
        mock_ry_config: Mock configuration
        mock_ry_session: Mock HTTP session

    Returns:
        RequirementYogiFetcher: Configured fetcher with mocked session
    """
    with (
        patch(
            "mcp_atlassian.requirement_yogi.client.Session",
            return_value=mock_ry_session,
        ),
        patch(
            "mcp_atlassian.requirement_yogi.client.configure_ssl_verification",
        ),
    ):
        fetcher = RequirementYogiFetcher(config=mock_ry_config)
        fetcher.session = mock_ry_session
        return fetcher


@pytest.fixture
def requirement_yogi_client_with_filter(mock_ry_config_with_filter, mock_ry_session):
    """
    Create a RequirementYogiFetcher with spaces filter and mocked session.

    Args:
        mock_ry_config_with_filter: Config with spaces filter
        mock_ry_session: Mock HTTP session

    Returns:
        RequirementYogiFetcher: Fetcher with spaces filter enabled
    """
    with (
        patch(
            "mcp_atlassian.requirement_yogi.client.Session",
            return_value=mock_ry_session,
        ),
        patch(
            "mcp_atlassian.requirement_yogi.client.configure_ssl_verification",
        ),
    ):
        fetcher = RequirementYogiFetcher(config=mock_ry_config_with_filter)
        fetcher.session = mock_ry_session
        return fetcher
