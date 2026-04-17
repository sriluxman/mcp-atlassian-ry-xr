"""Requirements Yogi FastMCP server instance and tool definitions."""

import json
import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from mcp_atlassian.requirement_yogi import RequirementYogiFetcher
from mcp_atlassian.requirement_yogi.constants import (
    DEFAULT_REQUIREMENTS_LIMIT,
    MAX_REQUIREMENTS_LIMIT,
)
from mcp_atlassian.servers.dependencies import get_requirement_yogi_fetcher
from mcp_atlassian.utils.decorators import check_write_access

logger = logging.getLogger(__name__)

requirement_yogi_mcp = FastMCP(
    name="Requirements Yogi MCP Service",
    instructions="Provides tools for interacting with Requirements Yogi (Confluence plugin).",
)


@requirement_yogi_mcp.tool(
    tags={"requirement_yogi", "read"},
    annotations={"title": "Get Requirement", "readOnlyHint": True},
)
async def get_requirement(
    ctx: Context,
    space_key: Annotated[
        str,
        Field(
            description="Confluence space key where the requirement resides (e.g., 'TYS', 'OCX', 'DEV')"
        ),
    ],
    requirement_key: Annotated[
        str,
        Field(
            description="Unique requirement key/ID (e.g., 'AR_ANSL_001', 'AS_017', 'REQ-001')"
        ),
    ],
) -> str:
    """Get a single requirement by space and key.

    Retrieves detailed information about a specific requirement from Requirements Yogi.

    Args:
        ctx: The FastMCP context.
        space_key: Confluence space key.
        requirement_key: Requirement key.

    Returns:
        JSON string representing the requirement object.

    Example:
        Get requirement AR_ANSL_001 from space TYS
        -> Returns full requirement details including title, description, properties, etc.
    """
    yogi_fetcher = await get_requirement_yogi_fetcher(ctx)
    requirement = yogi_fetcher.get_requirement(space_key, requirement_key)
    return json.dumps(requirement.to_simplified_dict(), indent=2, ensure_ascii=False)


@requirement_yogi_mcp.tool(
    tags={"requirement_yogi", "read"},
    annotations={"title": "List All Requirements (No Filter)", "readOnlyHint": True},
)
async def list_requirements(
    ctx: Context,
    space_key: Annotated[
        str,
        Field(
            description="Confluence space key to list requirements from (e.g., 'TYS', 'OCX', 'DEV')"
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description=f"Maximum number of requirements to return (1-{MAX_REQUIREMENTS_LIMIT})",
            default=DEFAULT_REQUIREMENTS_LIMIT,
            ge=1,
            le=MAX_REQUIREMENTS_LIMIT,
        ),
    ] = DEFAULT_REQUIREMENTS_LIMIT,
) -> str:
    """List ALL requirements in a Confluence space without any filtering.

    ⚠️ IMPORTANT: This tool lists ALL requirements in a space without filtering.
    If you need to filter by properties, keys, status, or any criteria,
    use the search_requirements tool instead.

    Use this tool ONLY when you want to:
    - Get a complete overview of all requirements in a space
    - Count total requirements without filters
    - Browse requirements without specific criteria

    For ANY filtering (Product, Category, Status, Owner, etc.), use search_requirements.

    Args:
        ctx: The FastMCP context.
        space_key: Confluence space key.
        limit: Maximum number of results to return.

    Returns:
        JSON string with results containing:
        - results: Array of ALL requirement objects (up to limit)
        - count: Total number of requirements in space
        - limit: Applied limit
        - offset: Starting offset (usually 0)

    Example:
        List first 50 requirements in space OCX (no filtering)
        -> Returns {"results": [...], "count": 150, "limit": 50, ...}
    """
    yogi_fetcher = await get_requirement_yogi_fetcher(ctx)
    response = yogi_fetcher.list_requirements(space_key, limit=limit)
    return json.dumps(response.to_simplified_dict(), indent=2, ensure_ascii=False)


@requirement_yogi_mcp.tool(
    tags={"requirement_yogi", "read", "primary"},
    annotations={"title": "Search & Filter Requirements", "readOnlyHint": True},
)
async def search_requirements(
    ctx: Context,
    space_key: Annotated[
        str,
        Field(
            description="Confluence space key to search requirements in (e.g., 'TYS', 'OCX', 'DEV')"
        ),
    ],
    query: Annotated[
        str,
        Field(
            description=(
                "Requirements Yogi search query using advanced syntax. "
                "PROPERTY FILTERING (most common): Use @PropertyName operator 'value' format. "
                "Examples: @Product = 'OpcUaCs', @Category = 'Functional', @Status = 'DRAFT'. "
                "KEY PATTERNS: key = 'REQ-001' (exact), key ~ 'REQ-%' (wildcard). "
                "BOOLEAN: Combine with AND, OR, NOT - e.g., @Product = 'AS' AND @Category = 'Functional'. "
                "OTHER: jira = 'JRA-21' (JIRA link), text ~ '%keyword%' (text search), FROM/TO (dependencies). "
                "Operators: = (equals), ~ (contains/wildcard with %), IS NULL (empty). "
                "All property names need @ prefix: @Product, @Category, @Priority, @Owner, @Type, @Status, etc."
            )
        ),
    ],
    limit: Annotated[
        int,
        Field(
            description=f"Maximum number of requirements to return (1-{MAX_REQUIREMENTS_LIMIT})",
            default=DEFAULT_REQUIREMENTS_LIMIT,
            ge=1,
            le=MAX_REQUIREMENTS_LIMIT,
        ),
    ] = DEFAULT_REQUIREMENTS_LIMIT,
) -> str:
    """🔍 PRIMARY TOOL: Search and filter requirements by any criteria.

    ⭐ USE THIS TOOL whenever you need to filter requirements by:
    - Properties: Product, Category, Status, Owner, Priority, Type, etc.
    - Keys or patterns
    - JIRA links
    - Text content
    - Dependencies
    - Any combination with boolean logic

    This tool uses Requirements Yogi's powerful query syntax (similar to SQL WHERE clause).
    It's much more efficient than fetching all requirements and filtering manually.

    Args:
        ctx: The FastMCP context.
        space_key: Confluence space key to search in.
        query: Search query using Requirements Yogi syntax (see field description for patterns).
        limit: Maximum number of results to return (default: 50, max: 200).

    Returns:
        JSON string with search results containing:
        - results: Array of matching requirement objects
        - count: Total number of matching requirements
        - explanation: Human-readable explanation of the query
        - aoSql: Internal SQL query (for debugging)
        - limit/offset: Pagination info

    Common Query Patterns:
        
        Filter by Product property:
            query = "@Product = 'OpcUaCs'"
        
        Filter by multiple properties:
            query = "@Product = 'AS' AND @Category = 'Functional'"
        
        Find requirements with specific key pattern:
            query = "key ~ 'PRD_%'"
        
        Find requirements by status:
            query = "@Status = 'DRAFT'"
        
        Find requirements linked to JIRA:
            query = "jira = 'OCX-11076'"
        
        Find requirements NOT linked to JIRA:
            query = "NOT (jira ~ '%')"
        
        Complex boolean query:
            query = "(@Product = 'OpcUaCs' OR @Product = 'AS') AND @Type = 'SYSTEM'"
        
        Search in text content:
            query = "text ~ '%installation%'"
        
        Find requirements with empty property:
            query = "@Owner IS NULL"

    Important Notes:
        ✅ Always use @ prefix for property names: @Product, @Category, @Status
        ✅ Use = for exact match, ~ for wildcard (with % as wildcard character)
        ✅ Use single quotes around values: 'OpcUaCs', 'Functional'
        ✅ Boolean operators: AND, OR, NOT (uppercase recommended)
        ✅ Parentheses for grouping: (@A = 'x' OR @B = 'y') AND @C = 'z'
        ⚠️  Property names are case-sensitive: @Product not @product
        ⚠️  Status is ACTIVE by default; add 'status = DELETED' for deleted requirements
    """
    yogi_fetcher = await get_requirement_yogi_fetcher(ctx)
    response = yogi_fetcher.list_requirements(space_key, limit=limit, query=query)
    return json.dumps(response.to_simplified_dict(), indent=2, ensure_ascii=False)


@requirement_yogi_mcp.tool(
    tags={"requirement_yogi", "write"},
    annotations={"title": "Create Requirement"},
)
@check_write_access
async def create_requirement(
    ctx: Context,
    space_key: Annotated[
        str,
        Field(
            description="Confluence space key where the requirement will be created"
        ),
    ],
    requirement_key: Annotated[
        str,
        Field(
            description="Unique requirement key/ID (must be unique within the space, e.g., 'REQ-NEW-001')"
        ),
    ],
    title: Annotated[
        str,
        Field(description="Requirement title (required)"),
    ],
    description: Annotated[
        str | None,
        Field(description="Requirement description (optional)", default=None),
    ] = None,
    properties: Annotated[
        dict | None,
        Field(
            description="Additional requirement properties as key-value pairs (optional)",
            default=None,
        ),
    ] = None,
) -> str:
    """Create a new requirement in Requirements Yogi.

    Creates a new requirement with the specified key and properties.

    Args:
        ctx: The FastMCP context.
        space_key: Confluence space key.
        requirement_key: Unique requirement key.
        title: Requirement title.
        description: Optional requirement description.
        properties: Optional additional properties.

    Returns:
        JSON string representing the created requirement.

    Raises:
        ValueError: If in read-only mode or if requirement key already exists.

    Example:
        Create requirement REQ-001 in space DEV with title "User Authentication"
        -> Creates the requirement and returns its full details
    """
    yogi_fetcher = await get_requirement_yogi_fetcher(ctx)

    # Build requirement data
    data = {"title": title}
    if description:
        data["description"] = description
    if properties:
        data.update(properties)

    requirement = yogi_fetcher.create_requirement(space_key, requirement_key, data)
    return json.dumps(requirement.to_simplified_dict(), indent=2, ensure_ascii=False)


@requirement_yogi_mcp.tool(
    tags={"requirement_yogi", "write"},
    annotations={"title": "Update Requirement"},
)
@check_write_access
async def update_requirement(
    ctx: Context,
    space_key: Annotated[
        str,
        Field(
            description="Confluence space key where the requirement exists"
        ),
    ],
    requirement_key: Annotated[
        str,
        Field(description="Requirement key to update"),
    ],
    title: Annotated[
        str | None,
        Field(description="New title (optional, leave empty to keep current)", default=None),
    ] = None,
    description: Annotated[
        str | None,
        Field(description="New description (optional, leave empty to keep current)", default=None),
    ] = None,
    properties: Annotated[
        dict | None,
        Field(
            description="Properties to update as key-value pairs (optional)",
            default=None,
        ),
    ] = None,
) -> str:
    """Update an existing requirement in Requirements Yogi.

    Updates one or more fields of an existing requirement.

    Args:
        ctx: The FastMCP context.
        space_key: Confluence space key.
        requirement_key: Requirement key.
        title: Optional new title.
        description: Optional new description.
        properties: Optional properties to update.

    Returns:
        JSON string representing the updated requirement.

    Raises:
        ValueError: If in read-only mode or if no update fields provided.

    Example:
        Update requirement AR_ANSL_001 in space TYS with new title "Updated Title"
        -> Updates the requirement and returns its full details
    """
    yogi_fetcher = await get_requirement_yogi_fetcher(ctx)

    # Build update data
    data = {}
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    if properties:
        data.update(properties)

    if not data:
        error_msg = "At least one field (title, description, or properties) must be provided for update"
        raise ValueError(error_msg)

    requirement = yogi_fetcher.update_requirement(space_key, requirement_key, data)
    return json.dumps(requirement.to_simplified_dict(), indent=2, ensure_ascii=False)


@requirement_yogi_mcp.tool(
    tags={"requirement_yogi", "write"},
    annotations={"title": "Delete Requirement"},
)
@check_write_access
async def delete_requirement(
    ctx: Context,
    space_key: Annotated[
        str,
        Field(
            description="Confluence space key where the requirement exists"
        ),
    ],
    requirement_key: Annotated[
        str,
        Field(description="Requirement key to delete"),
    ],
) -> str:
    """Delete a requirement from Requirements Yogi.

    Permanently deletes a requirement. This action cannot be undone.

    Args:
        ctx: The FastMCP context.
        space_key: Confluence space key.
        requirement_key: Requirement key to delete.

    Returns:
        JSON string indicating success or deletion result.

    Raises:
        ValueError: If in read-only mode.

    Example:
        Delete requirement REQ-TEMP-001 from space DEV
        -> Deletes the requirement and returns confirmation
    """
    yogi_fetcher = await get_requirement_yogi_fetcher(ctx)
    result = yogi_fetcher.delete_requirement(space_key, requirement_key)

    # Return success message if result is empty
    if not result:
        result = {
            "success": True,
            "message": f"Requirement '{requirement_key}' deleted from space '{space_key}'",
        }

    return json.dumps(result, indent=2, ensure_ascii=False)
