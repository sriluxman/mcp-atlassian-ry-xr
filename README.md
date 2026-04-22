# MCP Atlassian

![PyPI Version](https://img.shields.io/pypi/v/mcp-atlassian)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-atlassian)
![PePy - Total Downloads](https://static.pepy.tech/personalized-badge/mcp-atlassian?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Total%20Downloads)
[![Run Tests](https://github.com/sriluxman/mcp-atlassian-ry-xr/actions/workflows/tests.yml/badge.svg)](https://github.com/sriluxman/mcp-atlassian-ry-xr/actions/workflows/tests.yml)
![License](https://img.shields.io/github/license/sooperset/mcp-atlassian)
[![Docs](https://img.shields.io/badge/docs-github--pages-blue)](https://sriluxman.github.io/mcp-atlassian-ry-xr)

Model Context Protocol (MCP) server for Atlassian products (Confluence and Jira). Supports both Cloud and Server/Data Center deployments.

https://github.com/user-attachments/assets/35303504-14c6-4ae4-913b-7c25ea511c3e

<details>
<summary>Confluence Demo</summary>

https://github.com/user-attachments/assets/7fe9c488-ad0c-4876-9b54-120b666bb785

</details>

## Quick Start

### 1. Get Your API Token

Go to https://id.atlassian.com/manage-profile/security/api-tokens and create a token.

> For Server/Data Center, use a Personal Access Token instead. See [Authentication](https://sriluxman.github.io/mcp-atlassian-ry-xr/authentication).

### 2. Configure Your IDE

Add to your Claude Desktop or Cursor MCP configuration:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_api_token",
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

> **Server/Data Center users**: Use `JIRA_PERSONAL_TOKEN` instead of `JIRA_USERNAME` + `JIRA_API_TOKEN`. See [Authentication](https://sriluxman.github.io/mcp-atlassian-ry-xr/authentication) for details.

### 3. Start Using

Ask your AI assistant to:
- **"Find issues assigned to me in PROJ project"**
- **"Search Confluence for onboarding docs"**
- **"Create a bug ticket for the login issue"**
- **"Update the status of PROJ-123 to Done"**

## Documentation

Full documentation is available at **[sriluxman.github.io/mcp-atlassian-ry-xr](https://sriluxman.github.io/mcp-atlassian-ry-xr)**.

| Topic | Description |
|-------|-------------|
| [Installation](https://sriluxman.github.io/mcp-atlassian-ry-xr/installation) | uvx, Docker, pip, from source |
| [Authentication](https://sriluxman.github.io/mcp-atlassian-ry-xr/authentication) | API tokens, PAT, OAuth 2.0 |
| [Configuration](https://sriluxman.github.io/mcp-atlassian-ry-xr/configuration) | IDE setup, environment variables |
| [HTTP Transport](https://sriluxman.github.io/mcp-atlassian-ry-xr/http-transport) | SSE, streamable-http, multi-user |
| [Tools Reference](https://sriluxman.github.io/mcp-atlassian-ry-xr/tools-reference) | All Jira & Confluence tools |
| [Troubleshooting](https://sriluxman.github.io/mcp-atlassian-ry-xr/troubleshooting) | Common issues & debugging |

## Compatibility

| Product | Deployment | Support |
|---------|------------|---------|
| Confluence | Cloud | Fully supported |
| Confluence | Server/Data Center | Supported (v6.0+) |
| Jira | Cloud | Fully supported |
| Jira | Server/Data Center | Supported (v8.14+) |

## Key Tools

| Jira | Confluence |
|------|------------|
| `jira_search` - Search with JQL | `confluence_search` - Search with CQL |
| `jira_get_issue` - Get issue details | `confluence_get_page` - Get page content |
| `jira_create_issue` - Create issues | `confluence_create_page` - Create pages |
| `jira_update_issue` - Update issues | `confluence_update_page` - Update pages |
| `jira_transition_issue` - Change status | `confluence_add_comment` - Add comments |

**72 Jira & Confluence tools** — See [Tools Reference](https://sriluxman.github.io/mcp-atlassian-ry-xr/tools-reference) for the complete list.

## Requirements Yogi Integration

This fork extends MCP Atlassian with [Requirements Yogi](https://www.requirementsyogi.com/) support — 6 additional tools for managing requirements directly from your AI assistant. Requirements Yogi reuses your Confluence credentials; no separate login needed.

| Tool | Description |
|------|-------------|
| `requirement_yogi_search_requirements` | Advanced search with Requirements Yogi query syntax |
| `requirement_yogi_get_requirement` | Retrieve a requirement by key |
| `requirement_yogi_list_requirements` | List all requirements in a space |
| `requirement_yogi_create_requirement` | Create a new requirement |
| `requirement_yogi_update_requirement` | Update an existing requirement |
| `requirement_yogi_delete_requirement` | Delete a requirement |

Confluence credentials from your Quick Start configuration are automatically used. To restrict access to specific spaces, add:

```bash
REQUIREMENT_YOGI_SPACES_FILTER=TYS,OCX,DEV
```

See [Requirements Yogi Search Syntax](REQUIREMENTS_YOGI_SEARCH_SYNTAX.md) for the query language reference, and the [docs](docs/) for full tool documentation.

## Security

Never share API tokens. Keep `.env` files secure. See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

MIT - See [LICENSE](LICENSE). Not an official Atlassian product.
