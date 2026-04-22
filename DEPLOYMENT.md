# MCP Atlassian - Deployment Guide

## Overview

This guide explains how to deploy the MCP Atlassian server to another machine for use with VS Code or other MCP clients.

## Option 1: Using Pre-built Wheel (Recommended for Internal Use)

### On Build Machine

1. **Build the package:**
   ```bash
   cd mcp-atlassian-main
   uv build
   ```

   This creates:
   - `dist/mcp_atlassian-0.0.0-py3-none-any.whl`
   - `dist/mcp_atlassian-0.0.0.tar.gz`

2. **Copy the wheel file to a shared location:**
   - Network drive
   - Internal file server
   - Or copy directly to target machine

### On Target Machine

1. **Create `.vscode/mcp.json`:**
   ```json
   {
       "servers": {
           "mcp-atlassian": {
               "type": "stdio",
               "command": "uvx",
               "args": [
                   "--from",
                   "C:\\path\\to\\mcp_atlassian-0.0.0-py3-none-any.whl",
                   "mcp-atlassian",
                   "--env-file",
                   ".env"
               ]
           }
       },
       "inputs": []
   }
   ```

2. **Create `.env` file with your credentials:**
   ```env
   CONFLUENCE_URL=https://confluence.example-corp.com
   CONFLUENCE_USERNAME=your.email@company.com
   CONFLUENCE_PERSONAL_TOKEN=your_token_here
   ```

3. **Restart VS Code** - uvx will automatically install and run the server

## Option 2: Using PyPI (If Published)

If you publish to your company's private PyPI or public PyPI:

**mcp.json:**
```json
{
    "servers": {
        "mcp-atlassian": {
            "type": "stdio",
            "command": "uvx",
            "args": [
                "mcp-atlassian",
                "--env-file",
                ".env"
            ]
        }
    },
    "inputs": []
}
```

This is the cleanest - no paths needed!

## Option 3: Using Git Repository

If you push to an internal Git server:

**mcp.json:**
```json
{
    "servers": {
        "mcp-atlassian": {
            "type": "stdio",
            "command": "uvx",
            "args": [
                "--from",
                "git+https://your-git-server.com/org/mcp-atlassian.git",
                "mcp-atlassian",
                "--env-file",
                ".env"
            ]
        }
    },
    "inputs": []
}
```

## Requirements on Target Machine

- **Python 3.10+** must be installed
- **uv/uvx** must be installed:
  ```bash
  pip install uv
  ```
  Or download from: https://docs.astral.sh/uv/getting-started/installation/

## Verification

After setup, test the server:

```bash
uvx --from <your-source> mcp-atlassian --version
```

Should output: `mcp-atlassian, version 0.0.0`

## Available Tools

The server provides these Requirements Yogi tools:

1. **requirement_yogi_get_requirement** - Get single requirement details
2. **requirement_yogi_list_requirements** - List all requirements (no filter)
3. **requirement_yogi_search_requirements** - Search/filter requirements by criteria ⭐
4. **requirement_yogi_create_requirement** - Create new requirement
5. **requirement_yogi_update_requirement** - Update existing requirement
6. **requirement_yogi_delete_requirement** - Delete requirement

Plus Confluence and Jira tools if configured.

## Troubleshooting

### Tools not appearing

1. Check VS Code Output > GitHub Copilot Chat
2. Verify `.env` file exists and has correct credentials
3. Restart VS Code completely
4. Clear uvx cache: `uv cache clean`

### Authentication errors

1. Verify `CONFLUENCE_URL` doesn't have trailing slash
2. Check credentials are valid
3. For Confluence Cloud, use API token not password
4. For Confluence Server/DC, use Personal Access Token

### Search tool not visible

The `search_requirements` tool is properly registered. If you don't see it:
1. Restart VS Code (Ctrl+Shift+P → "Reload Window")
2. Check MCP connection status in VS Code
3. Verify the wheel/package is from the latest build

## Example Usage

After setup, you can use the search tool:

```
Tool: requirement_yogi_search_requirements
Args:
  space_key: "RPG"
  query: "@Product = 'OpcUaCs'"
  limit: 200
```

This searches for all requirements with Product property equal to 'OpcUaCs'.

## Support

For issues or questions:
- Check the main README.md
- Review REQUIREMENTS_YOGI_SEARCH_SYNTAX.md for query syntax
- See AGENTS.md for AI agent guidelines
