# Requirements Yogi Search Syntax Guide

This guide documents the powerful search query language for Requirements Yogi, which can be used with the `search_requirements` tool for efficient requirement filtering.

## Quick Start

```python
# Simple key search
query = "key = 'REQ-001'"

# Wildcard search
query = "key ~ 'AS_%'"

# Property search
query = "@Category = 'Functional'"

# Boolean combination
query = "key ~ 'AS_%' AND @Priority = 'High'"
```

## Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` or `==` | Strict equality | `key = 'REQ-001'` |
| `~` | Soft equality with wildcards (use `%`) | `key ~ 'REQ-%'` |
| `AND` | Boolean AND | `key ~ 'AS_%' AND @Priority = 'High'` |
| `OR` | Boolean OR | `@Category = 'Functional' OR @Category = 'Security'` |
| `NOT` | Boolean NOT | `NOT (jira ~ '%')` |
| `()` | Grouping | `(key ~ 'AS_%' OR key ~ 'BS_%') AND @Priority = 'High'` |
| `IS NULL` | Check for null value | `jira IS NULL` |
| `IS NOT NULL` | Check for non-null value | `baseline IS NOT NULL` |

## Fields

### Basic Fields

| Field | Description | Example |
|-------|-------------|---------|
| `key` | Requirement key (unique per space) | `key = 'REQ-001'` or `key ~ 'AS_%'` |
| `spaceKey` | Space key (case sensitive) | `spaceKey = 'OCX'` |
| `status` | Requirement status | `status = 'ACTIVE'` (default), `status = 'DELETED'`, `status = 'MOVED'` |
| `text` | Requirement content (excludes properties) | `text ~ '%authentication%'` |
| `page` | Page ID or version where requirement is defined | `page = 467382` |
| `pageHistory` | Page ID (all versions) | `pageHistory ~ 123` |
| `links` | Page where requirement is linked or defined | `links = 467382` |

### JIRA Integration

| Field | Description | Example |
|-------|-------------|---------|
| `jira` | JIRA issue linked to requirement | `jira = 'JRA-21'` |
| `jira@relationship` | JIRA issue with specific relationship | `jira@implements = 'OCX-11076'` |

**Examples:**
```
# Requirements linked to a JIRA issue
jira = 'OCX-11076'

# Requirements with "implements" relationship
jira@implements = 'PROJ-123'

# Requirements NOT linked to any JIRA issue
NOT (jira ~ '%')
```

### Properties

Properties use the `@` prefix followed by the property name.

**Examples:**
```
# Simple property match
@Category = 'Functional'

# Property with space (escape with backslash)
@Main\ Category = 'Security'

# External properties use ext@ prefix
ext@EstimatedHours = '8'

# Emoticons and special values
@Status = '(/)'  # Checkmark emoji

# User mentions
@Assignee = user('admin')
```

### Dependencies

| Field | Description | Example |
|-------|-------------|---------|
| `FROM` | Requirements referenced BY this key | `FROM = 'REQ-001'` |
| `TO` | Requirements that reference this key | `TO = 'REQ-001'` |
| `FROM@relationship` | Requirements with specific outgoing relationship | `FROM@refines = 'REQ-001'` |
| `TO@relationship` | Requirements with specific incoming relationship | `TO@implements = 'REQ-002'` |

**Examples:**
```
# Find requirements that reference REQ-001
TO = 'REQ-001'

# Find requirements referenced by REQ-001
FROM = 'REQ-001'

# Find requirements referenced by any AS requirement
FROM ~ 'AS-%'

# Find requirements "refined" by REQ-001
FROM@refines = 'REQ-001'
```

### Baselines

| Field | Description | Example |
|-------|-------------|---------|
| `baseline` | Baseline name or number | `baseline = 3` or `baseline = 'My Baseline'` |
| `baseline was` | Previous version baseline (since RY 3.2) | `baseline was 3` |

**Examples:**
```
# Requirements in baseline 3
baseline = 3

# Requirements currently in v4 that were also in v3
baseline = 4 AND baseline was 3

# Using variable (in traceability matrices)
baseline = $currentBaseline
```

### Special Functions

| Function | Description | Example |
|----------|-------------|---------|
| `isModified('version')` | Requirements modified since baseline | `isModified('7')` |
| `hasLastTest('result')` | Check last test result | `hasLastTest('%Success%')` |
| `hasTest(...)` | Check any test result | `hasTest('Passed')` |
| `user('username')` | Reference to user | `@Assignee = user('admin')` |

### Excel Integration

| Field | Description | Example |
|-------|-------------|---------|
| `excel` | Attachment ID from which requirements were imported | `excel = '48496653'` |

**Examples:**
```
# Requirements from specific Excel file
excel = '48496653'

# All requirements imported from Excel
excel ~ '%'
```

## Common Patterns

### By Requirement Key

```
# Exact match
key = 'REQ-001'

# Starts with prefix
key ~ 'AS_%'

# Multiple prefixes
key ~ 'AS_%' OR key ~ 'BS_%'
```

### By Content/Text

```
# Contains specific text
text ~ '%authentication%'

# Text ends with something
text ~ '% something'

# Text starts with something
text ~ 'something %'
```

### By Properties

```
# Single property
@Category = 'Functional'

# Multiple properties (AND)
@Category = 'Functional' AND @Priority = 'High'

# Multiple properties (OR)
@Category = 'Functional' OR @Category = 'Security'

# Property exists (not null)
@Category IS NOT NULL

# Property doesn't exist (null)
@Category IS NULL

# List property contains item
@Components = 'Authentication'
```

### By JIRA Integration

```
# Linked to specific issue
jira = 'OCX-11076'

# Linked to any JIRA issue
jira ~ '%'

# NOT linked to any JIRA issue
NOT (jira ~ '%')

# Specific relationship type
jira@implements = 'OCX-11076'
```

### By Dependencies

```
# Referenced by specific requirement
TO = 'REQ-001'

# References specific requirement
FROM = 'REQ-001'

# References any AS requirement
FROM ~ 'AS-%'

# Has any outgoing dependencies
FROM ~ '%'

# Has no outgoing dependencies
NOT (FROM ~ '%')
```

### Complex Queries

```
# High priority functional requirements starting with AS
key ~ 'AS_%' AND @Category = 'Functional' AND @Priority = 'High'

# Requirements linked to JIRA but not implemented
jira ~ '%' AND NOT (jira@implements ~ '%')

# Requirements modified since baseline without JIRA links
isModified('5') AND NOT (jira ~ '%')

# Requirements on specific page with functional category
page = 467382 AND @Category = 'Functional'

# Requirements with dependencies but no tests
(FROM ~ '%' OR TO ~ '%') AND NOT hasLastTest('%')
```

## Best Practices

### 1. Use Wildcards Efficiently

```
# Good: Specific prefix
key ~ 'AS_%'

# Less efficient: Too broad
text ~ '%a%'
```

### 2. Combine Filters for Precision

```
# Good: Multiple specific filters
key ~ 'AS_%' AND @Priority = 'High' AND NOT (jira ~ '%')

# Less precise: Single broad filter
key ~ '%'
```

### 3. Escape Special Characters

```
# Property with space
@Main\ Category = 'Security'

# Property with special character
@Cost\ \(USD\) = '1000'
```

### 4. Use Negation Wisely

```
# Good: Clear intent
NOT (jira ~ '%')

# Good: Complex negation
NOT (@Priority = 'Low' OR status = 'DELETED')
```

### 5. Leverage Boolean Logic

```
# Good: Group related conditions
(key ~ 'AS_%' OR key ~ 'BS_%') AND @Priority = 'High'

# Good: Clear precedence
key ~ 'AS_%' AND (@Priority = 'High' OR @Priority = 'Critical')
```

## API Usage

### Using the search_requirements Tool

```python
from mcp_atlassian.requirement_yogi import RequirementYogiFetcher

# Initialize fetcher
fetcher = RequirementYogiFetcher(config)

# Simple search
results = fetcher.list_requirements(
    space_key="OCX",
    query="key ~ 'AS_%'",
    limit=50
)

# Complex search
results = fetcher.list_requirements(
    space_key="OCX",
    query="@Category = 'Functional' AND @Priority = 'High' AND NOT (jira ~ '%')",
    limit=100
)

# Response structure
{
    "results": [
        {"key": "AS_001", "status": "ACTIVE", ...},
        {"key": "AS_002", "status": "ACTIVE", ...}
    ],
    "count": 150,  # Total matching requirements
    "limit": 100,   # Page size
    "offset": 0,    # Starting position
    "explanation": "Requirements with key starting with 'AS_' and with status 'ACTIVE'",
    "aoSql": "SELECT * FROM ..."  # Internal SQL query
}
```

### Agent Usage Examples

When working with an AI agent through MCP:

```
Agent: "Find all functional requirements in OCX space"
Tool: search_requirements(space_key="OCX", query="@Category = 'Functional'")

Agent: "Show AS requirements linked to OCX-11076"
Tool: search_requirements(space_key="OCX", query="key ~ 'AS_%' AND jira = 'OCX-11076'")

Agent: "Find high priority requirements without JIRA links"
Tool: search_requirements(space_key="OCX", query="@Priority = 'High' AND NOT (jira ~ '%')")

Agent: "List requirements that reference AS_001"
Tool: search_requirements(space_key="OCX", query="FROM = 'AS_001'")
```

## Performance Tips

1. **Add space context**: Always specify `space_key` - cross-space searches are slower
2. **Use specific key patterns**: `key ~ 'AS_%'` is faster than `text ~ '%AS%'`
3. **Limit result sets**: Use reasonable `limit` values (default: 50, max: 200)
4. **Filter by status**: Default is `ACTIVE` - explicit filtering helps performance
5. **Use indexed fields**: `key`, `status`, `jira` are indexed and faster than text search

## Limitations

1. **Cross-space searches**: Limited to single space per query
2. **Regex not supported**: Use `~` with `%` wildcards only
3. **Case sensitivity**: `spaceKey` is case-sensitive, most other fields are case-insensitive
4. **Page content**: `text` searches requirement content only, not full page content
5. **Historical data**: Some queries on baselines may be slower

## Version Differences

### Requirements Yogi 3.2+
- Added `baseline was` field
- Improved baseline queries

### Requirements Yogi 3.1+
- Changed `page ~` behavior to exact page only
- Added `pageHistory` and `links` fields
- More precise page-based filtering

### Requirements Yogi 2.4+
- Added emoticon support
- Added list property support
- Improved property formatting

## Reference

- [Official Search Syntax Documentation](https://docs.requirementyogi.com/data-center/search-syntax)
- [Requirements Yogi REST API](https://developer.requirementyogi.com/)
- [MCP Atlassian Documentation](https://sriluxman.github.io/mcp-atlassian-ry)

## Examples from BR Automation

Based on the OCX space structure:

```
# Find all AS (Architecture Specification) requirements
key ~ 'AS_%'

# Find requirements about command line interface
text ~ '%command line%'

# Find requirements related to export functionality
text ~ '%export%' AND key ~ 'AS_%'

# Find requirements on the OCX-11076 requirements page
page = 504827048

# Find requirements without proper categorization
@Category IS NULL OR @Priority IS NULL
```
