"""High-level fetcher for Requirements Yogi operations."""

import logging

from .requirements import RequirementsMixin

logger = logging.getLogger("mcp-atlassian")


class RequirementYogiFetcher(RequirementsMixin):
    """High-level facade for Requirements Yogi operations.

    This class combines all Requirements Yogi operation mixins into a single
    interface. It provides a simple way to interact with Requirements Yogi API.

    Example:
        >>> from mcp_atlassian.requirement_yogi import RequirementYogiFetcher
        >>> yogi = RequirementYogiFetcher()
        >>> requirement = yogi.get_requirement("TYS", "AR_ANSL_001")
        >>> requirements = yogi.list_requirements("OCX", limit=10)
    """

    pass
