"""Module for requirement CRUD operations."""

import logging
from typing import Any

from ..models.requirement_yogi import (
    Requirement,
    RequirementSearchResult,
)
from ..preprocessing.requirement_yogi import RequirementYogiPreprocessor
from .client import RequirementYogiClient
from .constants import (
    DEFAULT_REQUIREMENTS_LIMIT,
    HTTP_DELETE,
    HTTP_GET,
    HTTP_POST,
    HTTP_PUT,
    MAX_REQUIREMENTS_LIMIT,
)

logger = logging.getLogger("mcp-atlassian")


class RequirementsMixin(RequirementYogiClient):
    """Mixin for requirement CRUD operations.

    Provides methods to interact with Requirements Yogi's RequirementResource2 API.
    This is the space-scoped CRUD API for requirements.
    All methods return Pydantic models instead of raw dictionaries.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize mixin with preprocessor."""
        super().__init__(*args, **kwargs)
        base_url = self.config.confluence_url if self.config else ""
        self._preprocessor = RequirementYogiPreprocessor(base_url=base_url)

    def get_requirement(
        self,
        space_key: str,
        requirement_key: str,
    ) -> Requirement:
        """Get a single requirement by space and key.

        API: GET /rest/reqs/1/requirement2/{spaceKey}/{key}

        Args:
            space_key: Confluence space key (e.g., 'TYS', 'OCX')
            requirement_key: Requirement key (e.g., 'AR_ANSL_001', 'AS_017')

        Returns:
            Requirement model instance

        Raises:
            ValueError: If space is not in allowed filter
            MCPAtlassianAuthenticationError: If authentication fails
            HTTPError: If API request fails

        Example:
            >>> yogi.get_requirement("TYS", "AR_ANSL_001")
            Requirement(key='AR_ANSL_001', ...)
        """
        # Apply spaces filter if configured
        self._apply_spaces_filter(space_key)

        endpoint = f"/requirement2/{space_key}/{requirement_key}"
        logger.info(f"Getting requirement: space={space_key}, key={requirement_key}")

        result = self._request(HTTP_GET, endpoint)
        data = result if isinstance(result, dict) else {}
        return Requirement.from_api_response(data, preprocessor=self._preprocessor)

    def list_requirements(
        self,
        space_key: str,
        limit: int = DEFAULT_REQUIREMENTS_LIMIT,
        query: str | None = None,
    ) -> RequirementSearchResult:
        """List or search requirements in a space.

        API: GET /rest/reqs/1/requirement2/{spaceKey}

        Args:
            space_key: Confluence space key
            limit: Maximum number of requirements to return (1-200)
            query: Optional search query using Requirements Yogi search syntax.
                   Examples:
                   - "key ~ 'REQ-%'" - Requirements starting with REQ-
                   - "@Category = 'Functional'" - Requirements with Category property
                   - "text ~ '%authentication%'" - Requirements containing 'authentication'
                   - "jira = 'JRA-21'" - Requirements linked to JIRA issue
                   - "key ~ 'AS_%' AND @Priority = 'High'" - Complex boolean query

        Returns:
            RequirementSearchResult model with results, count, and metadata

        Raises:
            ValueError: If space is not in allowed filter or limit is invalid
            MCPAtlassianAuthenticationError: If authentication fails
            HTTPError: If API request fails

        Example:
            >>> yogi.list_requirements("OCX", limit=10)
            RequirementSearchResult(count=100, results=[...])
            >>> yogi.list_requirements("OCX", query="key ~ 'AS_%'")
            RequirementSearchResult(count=50, results=[...])
        """
        # Apply spaces filter if configured
        self._apply_spaces_filter(space_key)

        # Validate limit
        if limit < 1 or limit > MAX_REQUIREMENTS_LIMIT:
            error_msg = (
                f"Limit must be between 1 and {MAX_REQUIREMENTS_LIMIT}, got {limit}"
            )
            raise ValueError(error_msg)

        endpoint = f"/requirement2/{space_key}"
        params: dict[str, Any] = {"limit": limit}

        # Add search query if provided
        if query:
            params["q"] = query
            logger.info(
                f"Searching requirements: space={space_key}, query={query}, limit={limit}"
            )
        else:
            logger.info(f"Listing requirements: space={space_key}, limit={limit}")

        result = self._request(HTTP_GET, endpoint, params=params)

        # API returns dict with 'results', 'count', 'limit', 'offset', 'explanation'
        if isinstance(result, dict):
            return RequirementSearchResult.from_api_response(
                result, preprocessor=self._preprocessor
            )

        # Fallback for unexpected response format
        logger.warning(
            f"Unexpected response structure from list_requirements: {type(result)}"
        )
        fallback_data = {
            "results": result
            if isinstance(result, list)
            else [result]
            if result
            else [],
            "count": len(result) if isinstance(result, list) else (1 if result else 0),
            "limit": limit,
            "offset": 0,
        }
        return RequirementSearchResult.from_api_response(
            fallback_data, preprocessor=self._preprocessor
        )

    def create_requirement(
        self,
        space_key: str,
        requirement_key: str,
        data: dict[str, Any],
    ) -> Requirement:
        """Create a new requirement.

        API: POST /rest/reqs/1/requirement2/{spaceKey}/{key}

        Args:
            space_key: Confluence space key
            requirement_key: Unique requirement key (e.g., 'REQ-NEW-001')
            data: Requirement data (must include 'title', may include other fields)

        Returns:
            Created Requirement model instance

        Raises:
            ValueError: If space is not in allowed filter or data is invalid
            MCPAtlassianAuthenticationError: If authentication fails
            HTTPError: If API request fails

        Example:
            >>> yogi.create_requirement(
            ...     "DEV",
            ...     "REQ-001",
            ...     {"title": "New Requirement", "description": "Details here"}
            ... )
            Requirement(key='REQ-001', ...)
        """
        # Apply spaces filter if configured
        self._apply_spaces_filter(space_key)

        # Validate data
        if not data or "title" not in data:
            error_msg = "Requirement data must include 'title' field"
            raise ValueError(error_msg)

        endpoint = f"/requirement2/{space_key}/{requirement_key}"
        logger.info(
            f"Creating requirement: space={space_key}, key={requirement_key}, "
            f"title={data.get('title')}"
        )

        result = self._request(HTTP_POST, endpoint, json_data=data)
        response_data = result if isinstance(result, dict) else {}
        return Requirement.from_api_response(
            response_data, preprocessor=self._preprocessor
        )

    def update_requirement(
        self,
        space_key: str,
        requirement_key: str,
        data: dict[str, Any],
    ) -> Requirement:
        """Update an existing requirement.

        API: PUT /rest/reqs/1/requirement2/{spaceKey}/{key}

        Args:
            space_key: Confluence space key
            requirement_key: Requirement key to update
            data: Updated requirement data (fields to modify)

        Returns:
            Updated Requirement model instance

        Raises:
            ValueError: If space is not in allowed filter
            MCPAtlassianAuthenticationError: If authentication fails
            HTTPError: If API request fails

        Example:
            >>> yogi.update_requirement(
            ...     "DEV",
            ...     "REQ-001",
            ...     {"title": "Updated Title", "status": "Approved"}
            ... )
            Requirement(key='REQ-001', ...)
        """
        # Apply spaces filter if configured
        self._apply_spaces_filter(space_key)

        endpoint = f"/requirement2/{space_key}/{requirement_key}"
        logger.info(f"Updating requirement: space={space_key}, key={requirement_key}")

        result = self._request(HTTP_PUT, endpoint, json_data=data)
        response_data = result if isinstance(result, dict) else {}
        return Requirement.from_api_response(
            response_data, preprocessor=self._preprocessor
        )

    def delete_requirement(
        self,
        space_key: str,
        requirement_key: str,
    ) -> dict:
        """Delete a requirement.

        API: DELETE /rest/reqs/1/requirement2/{spaceKey}/{key}

        Args:
            space_key: Confluence space key
            requirement_key: Requirement key to delete

        Returns:
            Deletion result (usually empty dict or success message)

        Raises:
            ValueError: If space is not in allowed filter
            MCPAtlassianAuthenticationError: If authentication fails
            HTTPError: If API request fails

        Example:
            >>> yogi.delete_requirement("DEV", "REQ-001")
            {}
        """
        # Apply spaces filter if configured
        self._apply_spaces_filter(space_key)

        endpoint = f"/requirement2/{space_key}/{requirement_key}"
        logger.info(f"Deleting requirement: space={space_key}, key={requirement_key}")

        result = self._request(HTTP_DELETE, endpoint)
        return result if isinstance(result, dict) else {}

    def bulk_update_requirements(
        self,
        space_key: str,
        requirements_data: list[dict[str, Any]],
    ) -> dict:
        """Bulk update multiple requirements in a space.

        API: PUT /rest/reqs/1/requirement2/{spaceKey}

        Args:
            space_key: Confluence space key
            requirements_data: List of requirement update data

        Returns:
            Bulk update result

        Raises:
            ValueError: If space is not in allowed filter or data is invalid
            MCPAtlassianAuthenticationError: If authentication fails
            HTTPError: If API request fails

        Example:
            >>> yogi.bulk_update_requirements(
            ...     "DEV",
            ...     [
            ...         {"key": "REQ-001", "title": "Updated 1"},
            ...         {"key": "REQ-002", "title": "Updated 2"}
            ...     ]
            ... )
            {'updated': 2, 'failed': 0}
        """
        # Apply spaces filter if configured
        self._apply_spaces_filter(space_key)

        if not requirements_data:
            error_msg = "Requirements data list cannot be empty"
            raise ValueError(error_msg)

        endpoint = f"/requirement2/{space_key}"
        logger.info(
            f"Bulk updating requirements: space={space_key}, "
            f"count={len(requirements_data)}"
        )

        result = self._request(
            HTTP_PUT, endpoint, json_data={"requirements": requirements_data}
        )
        return result if isinstance(result, dict) else {}
