"""Base client module for Requirements Yogi API interactions."""

import logging
from typing import Any

from requests import Session
from requests.exceptions import HTTPError

from ..exceptions import MCPAtlassianAuthenticationError
from ..utils.logging import get_masked_session_headers, log_config_param, mask_sensitive
from ..utils.ssl import configure_ssl_verification
from .config import RequirementYogiConfig
from .constants import API_BASE_PATH

logger = logging.getLogger("mcp-atlassian")


class RequirementYogiClient:
    """Base client for Requirements Yogi REST API interactions.

    Requirements Yogi is a Confluence plugin that provides requirement management
    capabilities. This client handles authentication and HTTP requests to the
    Requirements Yogi REST API.
    """

    def __init__(self, config: RequirementYogiConfig | None = None) -> None:
        """Initialize the Requirements Yogi client.

        Args:
            config: Configuration for Requirements Yogi client. If None, will load
                from environment variables.

        Raises:
            ValueError: If configuration is invalid or environment variables are missing
        """
        self.config = config or RequirementYogiConfig.from_env()
        self.session = Session()

        # Configure authentication
        if self.config.auth_type == "pat":
            # Personal Access Token (Bearer)
            logger.debug(
                f"Initializing Requirements Yogi client with Token (PAT) auth. "
                f"URL: {self.config.confluence_url}, "
                f"Token (masked): {mask_sensitive(str(self.config.personal_token))}"
            )
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.personal_token}"
            })
        else:  # basic auth
            logger.debug(
                f"Initializing Requirements Yogi client with Basic auth. "
                f"URL: {self.config.confluence_url}, "
                f"Username: {self.config.username}, "
                f"API Token present: {bool(self.config.api_token)}"
            )
            self.session.auth = (self.config.username, self.config.api_token)

        # Standard headers for JSON API
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        # Add custom headers if provided
        if self.config.custom_headers:
            self.session.headers.update(self.config.custom_headers)

        # Configure proxies if provided
        if self.config.http_proxy or self.config.https_proxy:
            proxies = {}
            if self.config.http_proxy:
                proxies["http"] = self.config.http_proxy
            if self.config.https_proxy:
                proxies["https"] = self.config.https_proxy
            self.session.proxies.update(proxies)
            logger.debug(f"Configured proxies: {proxies}")

        # Configure SSL verification using the shared utility
        configure_ssl_verification(
            service_name="RequirementYogi",
            url=self.config.confluence_url,
            session=self.session,
            ssl_verify=self.config.ssl_verify,
            client_cert=self.config.client_cert,
            client_key=self.config.client_key,
            client_key_password=self.config.client_key_password,
        )

        logger.debug(
            f"Requirements Yogi client initialized. "
            f"Session headers (Authorization masked): "
            f"{get_masked_session_headers(dict(self.session.headers))}"
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        timeout: int = 30,
    ) -> dict | list | None:
        """Make authenticated request to Requirements Yogi API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base URL, starting with /)
            params: Query parameters
            json_data: JSON request body
            timeout: Request timeout in seconds

        Returns:
            JSON response data (dict or list), or None if empty response

        Raises:
            MCPAtlassianAuthenticationError: If authentication fails (401/403)
            HTTPError: If request fails with other HTTP error
            Exception: For other request errors
        """
        url = f"{self.config.full_base_url}{endpoint}"

        logger.debug(
            f"Requirements Yogi API request: {method} {url} "
            f"(params: {params}, has_body: {json_data is not None})"
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=timeout,
            )

            # Check for authentication errors
            if response.status_code in [401, 403]:
                error_msg = (
                    f"Authentication failed for Requirements Yogi API: "
                    f"{response.status_code} - {response.text}"
                )
                logger.error(error_msg)
                raise MCPAtlassianAuthenticationError(error_msg)

            # Raise for other HTTP errors
            response.raise_for_status()

            # Parse and return JSON response
            if response.content:
                result = response.json()
                logger.debug(
                    f"Requirements Yogi API response: {method} {url} -> "
                    f"{type(result).__name__} "
                    f"({len(result) if isinstance(result, list) else 'dict'})"
                )
                return result

            logger.debug(f"Requirements Yogi API response: {method} {url} -> empty")
            return None

        except HTTPError as e:
            logger.error(
                f"HTTP error during Requirements Yogi API request: {method} {url} - {e}",
                exc_info=True,
            )
            raise
        except Exception as e:
            logger.error(
                f"Error during Requirements Yogi API request: {method} {url} - {e}",
                exc_info=True,
            )
            raise

    def _apply_spaces_filter(self, space_key: str) -> None:
        """Check if space is allowed by filter configuration.

        Args:
            space_key: Space key to check

        Raises:
            ValueError: If space is not in the allowed filter list
        """
        if not self.config.spaces_filter:
            return

        allowed_spaces = [s.strip() for s in self.config.spaces_filter.split(",")]
        if space_key not in allowed_spaces:
            error_msg = (
                f"Space '{space_key}' is not in the allowed spaces filter: "
                f"{allowed_spaces}"
            )
            logger.warning(error_msg)
            raise ValueError(error_msg)
