"""Protocol definitions for Requirements Yogi operations."""

from typing import Any, Protocol, runtime_checkable

from ..models.requirement_yogi import Requirement, RequirementSearchResult


@runtime_checkable
class RequirementOperationsProto(Protocol):
    """Protocol for requirement CRUD operations."""

    def get_requirement(
        self,
        space_key: str,
        requirement_key: str,
    ) -> Requirement:
        """Get a single requirement."""
        ...

    def list_requirements(
        self,
        space_key: str,
        limit: int = 50,
        query: str | None = None,
    ) -> RequirementSearchResult:
        """List or search requirements in a space."""
        ...

    def create_requirement(
        self,
        space_key: str,
        requirement_key: str,
        data: dict[str, Any],
    ) -> Requirement:
        """Create a new requirement."""
        ...

    def update_requirement(
        self,
        space_key: str,
        requirement_key: str,
        data: dict[str, Any],
    ) -> Requirement:
        """Update an existing requirement."""
        ...

    def delete_requirement(
        self,
        space_key: str,
        requirement_key: str,
    ) -> dict:
        """Delete a requirement."""
        ...


@runtime_checkable
class BaselineOperationsProto(Protocol):
    """Protocol for baseline operations."""

    def list_baselines(
        self,
        space_key: str,
    ) -> list[dict]:
        """List all baselines in a space."""
        ...

    def get_baseline(
        self,
        space_key: str,
        version: str,
    ) -> dict:
        """Get a specific baseline."""
        ...

    def create_baseline(
        self,
        space_key: str,
        data: dict,
    ) -> dict:
        """Create a new baseline."""
        ...

    def update_baseline(
        self,
        space_key: str,
        version: str,
        data: dict,
    ) -> dict:
        """Update a baseline."""
        ...

    def delete_baseline(
        self,
        space_key: str,
        version: str,
    ) -> dict:
        """Delete a baseline."""
        ...
