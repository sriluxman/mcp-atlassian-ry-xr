"""Mock data for Requirements Yogi API responses.

This module provides realistic mock API responses that match the actual
Requirements Yogi RequirementResource2 API response format. These are
used across unit tests for models, client/mixins, and server tools.
"""

from typing import Any

# ============================================================================
# Single Requirement Response Mocks
# ============================================================================

MOCK_REQUIREMENT_RESPONSE: dict[str, Any] = {
    "key": "AR_ANSL_001",
    "spaceKey": "TYS",
    "status": "ACTIVE",
    "storageData": {
        "type": "STORAGE",
        "data": "<p>The system <strong>shall</strong> provide an ANSL interface for communication.</p>",
    },
    "properties": [
        {"key": "Category", "value": "Functional"},
        {"key": "Priority", "value": "High"},
        {"key": "Owner", "value": "Team Alpha"},
    ],
    "references": [
        {
            "key": "AS_017",
            "spaceKey": "TYS",
            "direction": "TO",
            "url": "/display/TYS/AS_017",
        },
        {
            "key": "AR_ANSL_002",
            "spaceKey": "TYS",
            "direction": "FROM",
            "url": "/display/TYS/AR_ANSL_002",
        },
    ],
    "issues": [
        {
            "issueKey": "OCX-11076",
            "issueId": 54321,
            "summary": "Implement ANSL interface",
            "status": "In Progress",
            "url": "https://jira.example.com/browse/OCX-11076",
        },
    ],
    "pageId": 123456789,
    "pageTitle": "ANSL Interface Requirements",
    "genericUrl": None,
}

MOCK_REQUIREMENT_MINIMAL: dict[str, Any] = {
    "key": "REQ-001",
    "spaceKey": "DEV",
    "status": "ACTIVE",
}

MOCK_REQUIREMENT_WITH_HTML: dict[str, Any] = {
    "key": "REQ-HTML-001",
    "spaceKey": "DEV",
    "status": "ACTIVE",
    "storageData": {
        "type": "STORAGE",
        "data": (
            "<h2>Feature Description</h2>"
            "<p>The system must support:</p>"
            "<ul>"
            "<li>Feature A with <strong>bold</strong> text</li>"
            "<li>Feature B with <em>italic</em> text</li>"
            "</ul>"
            "<p>See <a href='/pages/123'>related page</a> for details.</p>"
        ),
    },
    "properties": [
        {"key": "Category", "value": "Non-Functional"},
    ],
    "references": [],
    "issues": [],
    "pageId": 987654321,
    "pageTitle": "Feature Requirements",
}

MOCK_REQUIREMENT_EMPTY: dict[str, Any] = {}

MOCK_REQUIREMENT_NO_PROPERTIES: dict[str, Any] = {
    "key": "REQ-NOPROP-001",
    "spaceKey": "TEST",
    "status": "ACTIVE",
    "storageData": {
        "type": "STORAGE",
        "data": "<p>Simple requirement</p>",
    },
    "properties": [],
    "references": [],
    "issues": [],
}


# ============================================================================
# Search/List Response Mocks
# ============================================================================

MOCK_SEARCH_RESPONSE: dict[str, Any] = {
    "results": [
        {
            "key": "AS_001",
            "spaceKey": "TYS",
            "status": "ACTIVE",
            "storageData": {
                "type": "STORAGE",
                "data": "<p>Architecture specification 001</p>",
            },
            "properties": [
                {"key": "Category", "value": "Functional"},
            ],
            "references": [],
            "issues": [],
            "pageId": 111111,
            "pageTitle": "Architecture Specs",
        },
        {
            "key": "AS_002",
            "spaceKey": "TYS",
            "status": "ACTIVE",
            "storageData": {
                "type": "STORAGE",
                "data": "<p>Architecture specification 002</p>",
            },
            "properties": [
                {"key": "Category", "value": "Non-Functional"},
                {"key": "Priority", "value": "Medium"},
            ],
            "references": [
                {"key": "AS_001", "spaceKey": "TYS", "direction": "FROM"},
            ],
            "issues": [
                {"issueKey": "OCX-100", "summary": "Impl AS_002"},
            ],
            "pageId": 222222,
            "pageTitle": "Architecture Specs",
        },
        {
            "key": "AS_003",
            "spaceKey": "TYS",
            "status": "ACTIVE",
            "storageData": {
                "type": "STORAGE",
                "data": "<p>Architecture specification 003</p>",
            },
            "properties": [],
            "references": [],
            "issues": [],
            "pageId": 333333,
            "pageTitle": "Architecture Specs",
        },
    ],
    "count": 50,
    "limit": 3,
    "offset": 0,
    "explanation": "key ~ 'AS_%'",
    "aoSql": "SELECT * FROM requirements WHERE key LIKE 'AS_%'",
}

MOCK_SEARCH_EMPTY: dict[str, Any] = {
    "results": [],
    "count": 0,
    "limit": 50,
    "offset": 0,
    "explanation": "key = 'NONEXISTENT'",
}

MOCK_SEARCH_SINGLE: dict[str, Any] = {
    "results": [
        {
            "key": "REQ-SINGLE",
            "spaceKey": "DEV",
            "status": "ACTIVE",
            "properties": [{"key": "Priority", "value": "Critical"}],
            "references": [],
            "issues": [],
        },
    ],
    "count": 1,
    "limit": 50,
    "offset": 0,
    "explanation": "key = 'REQ-SINGLE'",
}


# ============================================================================
# Create/Update Response Mocks
# ============================================================================

MOCK_CREATE_RESPONSE: dict[str, Any] = {
    "key": "REQ-NEW-001",
    "spaceKey": "DEV",
    "status": "ACTIVE",
    "storageData": {
        "type": "STORAGE",
        "data": "<p>New requirement content</p>",
    },
    "properties": [],
    "references": [],
    "issues": [],
    "pageId": None,
    "pageTitle": None,
}

MOCK_UPDATE_RESPONSE: dict[str, Any] = {
    "key": "REQ-001",
    "spaceKey": "DEV",
    "status": "ACTIVE",
    "storageData": {
        "type": "STORAGE",
        "data": "<p>Updated requirement content</p>",
    },
    "properties": [
        {"key": "Category", "value": "Updated"},
    ],
    "references": [],
    "issues": [],
    "pageId": 123456,
    "pageTitle": "Requirements Page",
}


# ============================================================================
# Error Response Mocks
# ============================================================================

MOCK_AUTH_ERROR_RESPONSE: dict[str, Any] = {
    "status": 401,
    "message": "Authentication failed for Requirements Yogi API",
}

MOCK_NOT_FOUND_RESPONSE: dict[str, Any] = {
    "status": 404,
    "message": "Requirement not found",
}
