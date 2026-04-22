"""Unit tests for the RequirementYogiClient class."""

from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

from mcp_atlassian.exceptions import MCPAtlassianAuthenticationError
from mcp_atlassian.requirement_yogi.client import RequirementYogiClient
from mcp_atlassian.requirement_yogi.config import RequirementYogiConfig


class TestRequirementYogiClientInit:
    """Tests for RequirementYogiClient initialization."""

    def test_init_with_pat_auth(self):
        """Test initializing client with Personal Access Token."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
            personal_token="test_pat_token",
        )

        with (
            patch("mcp_atlassian.requirement_yogi.client.Session") as mock_session_cls,
            patch("mcp_atlassian.requirement_yogi.client.configure_ssl_verification"),
        ):
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            client = RequirementYogiClient(config=config)

            assert client.config == config
            # Verify Bearer token is set via headers.update
            mock_session.headers.update.assert_any_call(
                {"Authorization": "Bearer test_pat_token"}
            )

    def test_init_with_basic_auth(self):
        """Test initializing client with basic auth."""
        config = RequirementYogiConfig(
            confluence_url="https://example.atlassian.net/wiki",
            auth_type="basic",
            username="user@example.com",
            api_token="api_token",
        )

        with (
            patch("mcp_atlassian.requirement_yogi.client.Session") as mock_session_cls,
            patch("mcp_atlassian.requirement_yogi.client.configure_ssl_verification"),
        ):
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            client = RequirementYogiClient(config=config)

            assert client.config == config
            # Basic auth is set via session.auth
            assert mock_session.auth == ("user@example.com", "api_token")

    def test_init_from_env(self):
        """Test initializing client from environment variables."""
        with (
            patch(
                "mcp_atlassian.requirement_yogi.config.RequirementYogiConfig.from_env"
            ) as mock_from_env,
            patch("mcp_atlassian.requirement_yogi.client.Session"),
            patch("mcp_atlassian.requirement_yogi.client.configure_ssl_verification"),
        ):
            mock_config = MagicMock(spec=RequirementYogiConfig)
            mock_config.auth_type = "pat"
            mock_config.personal_token = "token"
            mock_config.confluence_url = "https://confluence.example.com"
            mock_config.custom_headers = None
            mock_config.http_proxy = None
            mock_config.https_proxy = None
            mock_config.ssl_verify = True
            mock_config.client_cert = None
            mock_config.client_key = None
            mock_config.client_key_password = None
            mock_from_env.return_value = mock_config

            client = RequirementYogiClient()

            mock_from_env.assert_called_once()
            assert client.config == mock_config

    def test_init_with_custom_headers(self):
        """Test initializing client with custom headers."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
            personal_token="token",
            custom_headers={"X-Custom-Header": "test-value"},
        )

        with (
            patch("mcp_atlassian.requirement_yogi.client.Session") as mock_session_cls,
            patch("mcp_atlassian.requirement_yogi.client.configure_ssl_verification"),
        ):
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            RequirementYogiClient(config=config)

            # Custom headers should be applied
            mock_session.headers.update.assert_any_call(
                {"X-Custom-Header": "test-value"}
            )

    def test_init_with_proxy_settings(self):
        """Test initializing client with proxy settings."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
            personal_token="token",
            http_proxy="http://proxy:8080",
            https_proxy="https://proxy:8443",
        )

        with (
            patch("mcp_atlassian.requirement_yogi.client.Session") as mock_session_cls,
            patch("mcp_atlassian.requirement_yogi.client.configure_ssl_verification"),
        ):
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            RequirementYogiClient(config=config)

            mock_session.proxies.update.assert_called_once_with(
                {"http": "http://proxy:8080", "https": "https://proxy:8443"}
            )


class TestRequirementYogiClientRequest:
    """Tests for RequirementYogiClient._request()."""

    def test_request_get(self, requirement_yogi_client, mock_ry_session):
        """Test making a GET request."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "test"}

        result = requirement_yogi_client._request("GET", "/test/endpoint")

        assert result == {"key": "test"}
        mock_ry_session.request.assert_called_once()

    def test_request_post_with_json(self, requirement_yogi_client, mock_ry_session):
        """Test making a POST request with JSON body."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": True}

        data = {"title": "Test"}
        result = requirement_yogi_client._request(
            "POST", "/test/create", json_data=data
        )

        assert result == {"created": True}
        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["json"] == data

    def test_request_with_params(self, requirement_yogi_client, mock_ry_session):
        """Test making a request with query parameters."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        params = {"limit": 10, "q": "key ~ 'AS_%'"}
        requirement_yogi_client._request("GET", "/test", params=params)

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["params"] == params

    def test_request_401_raises_auth_error(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that 401 response raises MCPAtlassianAuthenticationError."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with pytest.raises(MCPAtlassianAuthenticationError):
            requirement_yogi_client._request("GET", "/test")

    def test_request_403_raises_auth_error(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that 403 response raises MCPAtlassianAuthenticationError."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        with pytest.raises(MCPAtlassianAuthenticationError):
            requirement_yogi_client._request("GET", "/test")

    def test_request_http_error_propagated(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that HTTP errors are propagated."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = HTTPError("Server Error")

        with pytest.raises(HTTPError):
            requirement_yogi_client._request("GET", "/test")

    def test_request_empty_response(self, requirement_yogi_client, mock_ry_session):
        """Test handling of empty response content."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 204
        mock_response.content = b""

        result = requirement_yogi_client._request("DELETE", "/test")
        assert result is None


class TestApplySpacesFilter:
    """Tests for RequirementYogiClient._apply_spaces_filter()."""

    def test_filter_allows_valid_space(self, requirement_yogi_client_with_filter):
        """Test that valid spaces pass the filter."""
        # Should not raise
        requirement_yogi_client_with_filter._apply_spaces_filter("TYS")
        requirement_yogi_client_with_filter._apply_spaces_filter("OCX")
        requirement_yogi_client_with_filter._apply_spaces_filter("DEV")

    def test_filter_blocks_invalid_space(self, requirement_yogi_client_with_filter):
        """Test that invalid spaces are blocked."""
        with pytest.raises(ValueError, match="not in the allowed spaces filter"):
            requirement_yogi_client_with_filter._apply_spaces_filter("BLOCKED")

    def test_no_filter_allows_all(self, requirement_yogi_client):
        """Test that without filter, all spaces pass."""
        # Should not raise for any space
        requirement_yogi_client._apply_spaces_filter("ANY_SPACE")
        requirement_yogi_client._apply_spaces_filter("RANDOM")
