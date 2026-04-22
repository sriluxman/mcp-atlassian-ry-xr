"""
Common Requirements Yogi entity models.
This module provides Pydantic models for Requirements Yogi sub-entities
such as storage data, properties, and references.
"""

import logging
from typing import Any

from ..base import ApiModel
from ..constants import EMPTY_STRING

logger = logging.getLogger(__name__)


class RequirementStorageData(ApiModel):
    """
    Model representing the storage data content of a requirement.

    Requirements Yogi stores requirement content as HTML in a storageData object
    with a type identifier and the HTML data string.
    """

    type: str = EMPTY_STRING
    data: str = EMPTY_STRING

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "RequirementStorageData":
        """
        Create a RequirementStorageData from an API response.

        Args:
            data: The storageData dict from the API response

        Returns:
            A RequirementStorageData instance
        """
        if not data:
            return cls()

        return cls(
            type=data.get("type", EMPTY_STRING),
            data=data.get("data", EMPTY_STRING),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        result: dict[str, Any] = {}
        if self.type:
            result["type"] = self.type
        if self.data:
            result["data"] = self.data
        return result


class RequirementProperty(ApiModel):
    """
    Model representing a requirement property (custom field).

    Properties are user-defined key-value pairs on requirements,
    such as @Category, @Priority, @Status, etc.
    """

    key: str = EMPTY_STRING
    value: str = EMPTY_STRING

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "RequirementProperty":
        """
        Create a RequirementProperty from an API response.

        Args:
            data: A property dict with 'key' and 'value' fields

        Returns:
            A RequirementProperty instance
        """
        if not data:
            return cls()

        return cls(
            key=data.get("key", EMPTY_STRING),
            value=data.get("value", EMPTY_STRING),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        return {"key": self.key, "value": self.value}


class RequirementReference(ApiModel):
    """
    Model representing a reference between requirements (dependency/trace).

    References represent traceability links between requirements. They have
    a direction (FROM = referenced by, TO = references) and a target key.
    """

    key: str = EMPTY_STRING
    space_key: str = EMPTY_STRING
    direction: str = EMPTY_STRING  # "FROM" or "TO"
    url: str | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "RequirementReference":
        """
        Create a RequirementReference from an API response.

        Args:
            data: A reference dict from the API

        Returns:
            A RequirementReference instance
        """
        if not data:
            return cls()

        return cls(
            key=data.get("key", EMPTY_STRING),
            space_key=data.get("spaceKey", EMPTY_STRING),
            direction=data.get("direction", EMPTY_STRING),
            url=data.get("url"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        result: dict[str, Any] = {"key": self.key}
        if self.space_key:
            result["space_key"] = self.space_key
        if self.direction:
            result["direction"] = self.direction
        if self.url:
            result["url"] = self.url
        return result


class RequirementJiraLink(ApiModel):
    """
    Model representing a JIRA issue link on a requirement.
    """

    issue_key: str = EMPTY_STRING
    issue_id: int | None = None
    summary: str | None = None
    status: str | None = None
    url: str | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "RequirementJiraLink":
        """
        Create a RequirementJiraLink from an API response.

        Args:
            data: A JIRA link dict from the API

        Returns:
            A RequirementJiraLink instance
        """
        if not data:
            return cls()

        return cls(
            issue_key=data.get("issueKey", data.get("key", EMPTY_STRING)),
            issue_id=data.get("issueId"),
            summary=data.get("summary"),
            status=data.get("status"),
            url=data.get("url"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        result: dict[str, Any] = {"issue_key": self.issue_key}
        if self.summary:
            result["summary"] = self.summary
        if self.status:
            result["status"] = self.status
        if self.url:
            result["url"] = self.url
        return result
