"""
Requirements Yogi requirement model.
This module provides the Pydantic model for a Requirements Yogi requirement,
including all sub-entities (properties, references, JIRA links, storage data).
"""

import logging
from typing import Any

from pydantic import Field

from ..base import ApiModel
from ..constants import EMPTY_STRING
from .common import (
    RequirementJiraLink,
    RequirementProperty,
    RequirementReference,
    RequirementStorageData,
)

logger = logging.getLogger(__name__)


class Requirement(ApiModel):
    """
    Model representing a Requirements Yogi requirement.

    This is the core model for a single requirement. It maps from the
    RequirementResource2 API response format and provides a simplified
    dictionary output for API consumers.
    """

    key: str = EMPTY_STRING
    space_key: str = EMPTY_STRING
    status: str = "ACTIVE"
    storage_data: RequirementStorageData | None = None
    properties: list[RequirementProperty] = Field(default_factory=list)
    references: list[RequirementReference] = Field(default_factory=list)
    jira_links: list[RequirementJiraLink] = Field(default_factory=list)
    page_id: int | None = None
    page_title: str | None = None
    generic_url: str | None = None
    content_markdown: str | None = None  # Preprocessed markdown content

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "Requirement":
        """
        Create a Requirement from a Requirements Yogi API response.

        Args:
            data: The requirement data from the RequirementResource2 API
            **kwargs: Additional context parameters:
                - preprocessor: Optional preprocessor for HTML→markdown conversion

        Returns:
            A Requirement instance
        """
        if not data:
            return cls()

        # Parse storage data
        storage_data = None
        if sd := data.get("storageData"):
            storage_data = RequirementStorageData.from_api_response(sd)

        # Parse properties list
        properties = []
        for prop in data.get("properties", []):
            properties.append(RequirementProperty.from_api_response(prop))

        # Parse references (dependencies/traces)
        references = []
        for ref in data.get("references", []):
            references.append(RequirementReference.from_api_response(ref))

        # Parse JIRA links
        jira_links = []
        for jira in data.get("issues", data.get("jiraLinks", [])):
            jira_links.append(RequirementJiraLink.from_api_response(jira))

        # Parse page info
        page_id = data.get("pageId")
        page_title = data.get("pageTitle")

        # Preprocess HTML content to markdown if preprocessor provided
        content_markdown = None
        preprocessor = kwargs.get("preprocessor")
        if preprocessor and storage_data and storage_data.data:
            try:
                _, content_markdown = preprocessor.process_html_content(
                    storage_data.data
                )
            except Exception as e:
                logger.warning(f"Error preprocessing requirement content: {e}")

        return cls(
            key=data.get("key", EMPTY_STRING),
            space_key=data.get("spaceKey", EMPTY_STRING),
            status=data.get("status", "ACTIVE"),
            storage_data=storage_data,
            properties=properties,
            references=references,
            jira_links=jira_links,
            page_id=page_id,
            page_title=page_title,
            generic_url=data.get("genericUrl"),
            content_markdown=content_markdown,
        )

    def get_property(self, key: str) -> str | None:
        """
        Get a property value by key.

        Args:
            key: The property key to look up

        Returns:
            The property value, or None if not found
        """
        for prop in self.properties:
            if prop.key == key:
                return prop.value
        return None

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        result: dict[str, Any] = {
            "key": self.key,
            "space_key": self.space_key,
            "status": self.status,
        }

        # Add content - prefer markdown, fall back to storage data
        if self.content_markdown:
            result["content"] = self.content_markdown
        elif self.storage_data and self.storage_data.data:
            result["storage_data"] = self.storage_data.to_simplified_dict()

        # Add properties as a flat key-value map for easy consumption
        if self.properties:
            result["properties"] = {
                prop.key: prop.value for prop in self.properties
            }

        # Add references
        if self.references:
            result["references"] = [
                ref.to_simplified_dict() for ref in self.references
            ]

        # Add JIRA links
        if self.jira_links:
            result["jira_links"] = [
                jira.to_simplified_dict() for jira in self.jira_links
            ]

        # Add page info
        if self.page_id is not None:
            result["page_id"] = self.page_id
        if self.page_title:
            result["page_title"] = self.page_title

        # Add generic URL
        if self.generic_url:
            result["generic_url"] = self.generic_url

        return result
