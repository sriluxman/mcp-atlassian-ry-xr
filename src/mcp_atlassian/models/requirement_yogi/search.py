"""
Requirements Yogi search result models.
This module provides Pydantic models for Requirements Yogi search/list results.
"""

import logging
from typing import Any

from pydantic import Field, model_validator

from ..base import ApiModel
from .requirement import Requirement

logger = logging.getLogger(__name__)


class RequirementSearchResult(ApiModel):
    """
    Model representing a Requirements Yogi search/list result.

    This wraps the paginated response from the list/search requirements API,
    containing the list of requirements along with pagination metadata.
    """

    results: list[Requirement] = Field(default_factory=list)
    count: int = 0
    limit: int = 0
    offset: int = 0
    explanation: str | None = None
    ao_sql: str | None = None  # Internal SQL query (for debugging)

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "RequirementSearchResult":
        """
        Create a RequirementSearchResult from the API response.

        Args:
            data: The search result data from the Requirements Yogi API
            **kwargs: Additional context parameters passed to Requirement models:
                - preprocessor: Optional preprocessor for HTML→markdown conversion

        Returns:
            A RequirementSearchResult instance
        """
        if not data:
            return cls()

        # Convert each result item to a Requirement model
        results = []
        for item in data.get("results", []):
            results.append(Requirement.from_api_response(item, **kwargs))

        return cls(
            results=results,
            count=data.get("count", 0),
            limit=data.get("limit", 0),
            offset=data.get("offset", 0),
            explanation=data.get("explanation"),
            ao_sql=data.get("aoSql"),
        )

    @model_validator(mode="after")
    def validate_search_result(self) -> "RequirementSearchResult":
        """Validate the search result and log warnings if needed."""
        if self.count > 0 and not self.results:
            logger.warning(
                "Search found %d requirements but no result data was returned",
                self.count,
            )
        return self

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        result: dict[str, Any] = {
            "results": [req.to_simplified_dict() for req in self.results],
            "count": self.count,
            "limit": self.limit,
            "offset": self.offset,
        }

        if self.explanation:
            result["explanation"] = self.explanation
        if self.ao_sql:
            result["ao_sql"] = self.ao_sql

        return result
