"""Configuration module for Requirements Yogi client."""

import logging
import os
from dataclasses import dataclass
from typing import Literal

from ..utils.env import is_env_ssl_verify

logger = logging.getLogger("mcp-atlassian")


@dataclass
class RequirementYogiConfig:
    """Requirements Yogi API configuration.

    Requirements Yogi is a Confluence plugin, so it uses Confluence authentication.
    This config reuses Confluence URL and authentication settings.
    """

    confluence_url: str  # Base URL for Confluence instance
    auth_type: Literal[
        "basic", "pat"
    ]  # Authentication type (OAuth not directly supported by Yogi)
    username: str | None = None  # Email or username (for basic auth)
    api_token: str | None = None  # API token (for basic auth)
    personal_token: str | None = None  # Personal access token (Server/DC)
    ssl_verify: bool = True  # Whether to verify SSL certificates
    spaces_filter: str | None = None  # Comma-separated list of space keys to filter
    base_path: str = "/rest/reqs/1"  # Requirements Yogi API base path
    http_proxy: str | None = None  # HTTP proxy URL
    https_proxy: str | None = None  # HTTPS proxy URL
    no_proxy: str | None = None  # Comma-separated list of hosts to bypass proxy
    socks_proxy: str | None = None  # SOCKS proxy URL
    custom_headers: dict[str, str] | None = None  # Custom HTTP headers
    client_cert: str | None = None  # Client certificate file path
    client_key: str | None = None  # Client private key file path
    client_key_password: str | None = None  # Password for encrypted private key

    @property
    def full_base_url(self) -> str:
        """Get full Requirements Yogi API base URL.

        Returns:
            Complete API base URL (e.g., https://confluence.example.com/rest/reqs/1)
        """
        return f"{self.confluence_url.rstrip('/')}{self.base_path}"

    def is_auth_configured(self) -> bool:
        """Check if authentication is properly configured.

        Returns:
            True if valid authentication credentials are present
        """
        if self.auth_type == "pat":
            return bool(self.personal_token)
        elif self.auth_type == "basic":
            return bool(self.username and self.api_token)
        return False

    @classmethod
    def from_env(cls) -> "RequirementYogiConfig":
        """Create configuration from environment variables.

        Uses CONFLUENCE_* environment variables since Requirements Yogi
        is a Confluence plugin.

        Returns:
            RequirementYogiConfig with values from environment

        Raises:
            ValueError: If required environment variables are missing
        """
        url = os.getenv("CONFLUENCE_URL")
        if not url:
            error_msg = "Missing required CONFLUENCE_URL environment variable"
            raise ValueError(error_msg)

        # Get authentication credentials
        username = os.getenv("CONFLUENCE_USERNAME")
        api_token = os.getenv("CONFLUENCE_API_TOKEN")
        personal_token = os.getenv("CONFLUENCE_PERSONAL_TOKEN")

        # Determine authentication type
        if personal_token:
            auth_type = "pat"
            logger.debug(
                "Using Personal Access Token authentication for Requirements Yogi"
            )
        elif username and api_token:
            auth_type = "basic"
            logger.debug("Using Basic authentication for Requirements Yogi")
        else:
            error_msg = (
                "Missing authentication credentials. Provide either:\n"
                "  - CONFLUENCE_PERSONAL_TOKEN (for Server/Data Center)\n"
                "  - CONFLUENCE_USERNAME + CONFLUENCE_API_TOKEN (for Cloud)"
            )
            raise ValueError(error_msg)

        # SSL verification
        ssl_verify = is_env_ssl_verify("CONFLUENCE_SSL_VERIFY")

        # Optional space filtering
        spaces_filter = os.getenv("REQUIREMENT_YOGI_SPACES_FILTER")

        # Proxy settings
        http_proxy = os.getenv("CONFLUENCE_HTTP_PROXY")
        https_proxy = os.getenv("CONFLUENCE_HTTPS_PROXY")
        no_proxy = os.getenv("CONFLUENCE_NO_PROXY")
        socks_proxy = os.getenv("CONFLUENCE_SOCKS_PROXY")

        # Client certificate settings
        client_cert = os.getenv("CONFLUENCE_CLIENT_CERT")
        client_key = os.getenv("CONFLUENCE_CLIENT_KEY")
        client_key_password = os.getenv("CONFLUENCE_CLIENT_KEY_PASSWORD")

        return cls(
            confluence_url=url,
            auth_type=auth_type,
            username=username,
            api_token=api_token,
            personal_token=personal_token,
            ssl_verify=ssl_verify,
            spaces_filter=spaces_filter,
            http_proxy=http_proxy,
            https_proxy=https_proxy,
            no_proxy=no_proxy,
            socks_proxy=socks_proxy,
            client_cert=client_cert,
            client_key=client_key,
            client_key_password=client_key_password,
        )
