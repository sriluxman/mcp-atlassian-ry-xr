"""Unit tests for the RequirementYogiConfig class."""

import os
from unittest.mock import patch

import pytest

from mcp_atlassian.requirement_yogi.config import RequirementYogiConfig


class TestRequirementYogiConfigFromEnv:
    """Tests for RequirementYogiConfig.from_env()."""

    def test_from_env_with_pat(self):
        """Test creating config from env with Personal Access Token."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_URL": "https://confluence.example.com",
                "CONFLUENCE_PERSONAL_TOKEN": "pat_token_12345",
            },
            clear=True,
        ):
            config = RequirementYogiConfig.from_env()
            assert config.confluence_url == "https://confluence.example.com"
            assert config.auth_type == "pat"
            assert config.personal_token == "pat_token_12345"
            assert config.username is None
            assert config.api_token is None

    def test_from_env_with_basic_auth(self):
        """Test creating config from env with basic auth credentials."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_URL": "https://example.atlassian.net/wiki",
                "CONFLUENCE_USERNAME": "user@example.com",
                "CONFLUENCE_API_TOKEN": "api_token_xyz",
            },
            clear=True,
        ):
            config = RequirementYogiConfig.from_env()
            assert config.confluence_url == "https://example.atlassian.net/wiki"
            assert config.auth_type == "basic"
            assert config.username == "user@example.com"
            assert config.api_token == "api_token_xyz"

    def test_from_env_pat_takes_priority(self):
        """Test that PAT auth takes priority when both are provided."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_URL": "https://confluence.example.com",
                "CONFLUENCE_USERNAME": "user@example.com",
                "CONFLUENCE_API_TOKEN": "api_token",
                "CONFLUENCE_PERSONAL_TOKEN": "pat_token",
            },
            clear=True,
        ):
            config = RequirementYogiConfig.from_env()
            assert config.auth_type == "pat"
            assert config.personal_token == "pat_token"

    def test_from_env_missing_url(self):
        """Test that from_env raises ValueError when URL is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="Missing required CONFLUENCE_URL"
            ):
                RequirementYogiConfig.from_env()

    def test_from_env_missing_auth(self):
        """Test that from_env raises ValueError when no auth is provided."""
        with patch.dict(
            os.environ,
            {"CONFLUENCE_URL": "https://confluence.example.com"},
            clear=True,
        ):
            with pytest.raises(
                ValueError, match="Missing authentication credentials"
            ):
                RequirementYogiConfig.from_env()

    def test_from_env_with_spaces_filter(self):
        """Test that spaces filter is loaded from environment."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_URL": "https://confluence.example.com",
                "CONFLUENCE_PERSONAL_TOKEN": "pat_token",
                "REQUIREMENT_YOGI_SPACES_FILTER": "TYS,OCX,DEV",
            },
            clear=True,
        ):
            config = RequirementYogiConfig.from_env()
            assert config.spaces_filter == "TYS,OCX,DEV"

    def test_from_env_without_spaces_filter(self):
        """Test that spaces filter is None when not set."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_URL": "https://confluence.example.com",
                "CONFLUENCE_PERSONAL_TOKEN": "pat_token",
            },
            clear=True,
        ):
            config = RequirementYogiConfig.from_env()
            assert config.spaces_filter is None

    def test_from_env_with_proxy_settings(self):
        """Test that proxy settings are loaded from environment."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_URL": "https://confluence.example.com",
                "CONFLUENCE_PERSONAL_TOKEN": "pat_token",
                "CONFLUENCE_HTTP_PROXY": "http://proxy:8080",
                "CONFLUENCE_HTTPS_PROXY": "https://proxy:8443",
                "CONFLUENCE_NO_PROXY": "localhost,127.0.0.1",
            },
            clear=True,
        ):
            config = RequirementYogiConfig.from_env()
            assert config.http_proxy == "http://proxy:8080"
            assert config.https_proxy == "https://proxy:8443"
            assert config.no_proxy == "localhost,127.0.0.1"

    def test_from_env_with_client_cert(self):
        """Test that client certificate settings are loaded from environment."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_URL": "https://confluence.example.com",
                "CONFLUENCE_PERSONAL_TOKEN": "pat_token",
                "CONFLUENCE_CLIENT_CERT": "/path/to/cert.pem",
                "CONFLUENCE_CLIENT_KEY": "/path/to/key.pem",
                "CONFLUENCE_CLIENT_KEY_PASSWORD": "certpass",
            },
            clear=True,
        ):
            config = RequirementYogiConfig.from_env()
            assert config.client_cert == "/path/to/cert.pem"
            assert config.client_key == "/path/to/key.pem"
            assert config.client_key_password == "certpass"


class TestRequirementYogiConfigProperties:
    """Tests for RequirementYogiConfig properties and methods."""

    def test_full_base_url(self):
        """Test full_base_url property."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
            personal_token="token",
        )
        assert (
            config.full_base_url
            == "https://confluence.example.com/rest/reqs/1"
        )

    def test_full_base_url_strips_trailing_slash(self):
        """Test that trailing slash in URL is handled."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com/",
            auth_type="pat",
            personal_token="token",
        )
        assert (
            config.full_base_url
            == "https://confluence.example.com/rest/reqs/1"
        )

    def test_is_auth_configured_pat(self):
        """Test is_auth_configured with PAT."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
            personal_token="token",
        )
        assert config.is_auth_configured() is True

    def test_is_auth_configured_pat_missing(self):
        """Test is_auth_configured with PAT missing."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
        )
        assert config.is_auth_configured() is False

    def test_is_auth_configured_basic(self):
        """Test is_auth_configured with basic auth."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="basic",
            username="user",
            api_token="token",
        )
        assert config.is_auth_configured() is True

    def test_is_auth_configured_basic_missing_username(self):
        """Test is_auth_configured with basic auth missing username."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="basic",
            api_token="token",
        )
        assert config.is_auth_configured() is False

    def test_is_auth_configured_basic_missing_token(self):
        """Test is_auth_configured with basic auth missing token."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="basic",
            username="user",
        )
        assert config.is_auth_configured() is False

    def test_default_base_path(self):
        """Test default base_path value."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
            personal_token="token",
        )
        assert config.base_path == "/rest/reqs/1"

    def test_custom_base_path(self):
        """Test custom base_path override."""
        config = RequirementYogiConfig(
            confluence_url="https://confluence.example.com",
            auth_type="pat",
            personal_token="token",
            base_path="/rest/reqs/2",
        )
        assert config.full_base_url == "https://confluence.example.com/rest/reqs/2"
