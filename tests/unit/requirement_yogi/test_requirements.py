"""Unit tests for the RequirementsMixin class."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.exceptions import MCPAtlassianAuthenticationError
from mcp_atlassian.models.requirement_yogi import (
    Requirement,
    RequirementSearchResult,
)
from mcp_atlassian.requirement_yogi.constants import MAX_REQUIREMENTS_LIMIT
from tests.fixtures.requirement_yogi_mocks import (
    MOCK_CREATE_RESPONSE,
    MOCK_REQUIREMENT_RESPONSE,
    MOCK_SEARCH_RESPONSE,
    MOCK_UPDATE_RESPONSE,
)


class TestGetRequirement:
    """Tests for RequirementsMixin.get_requirement()."""

    def test_get_requirement_returns_model(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that get_requirement returns a Requirement model."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        result = requirement_yogi_client.get_requirement("TYS", "AR_ANSL_001")

        assert isinstance(result, Requirement)
        assert result.key == "AR_ANSL_001"
        assert result.space_key == "TYS"

    def test_get_requirement_api_endpoint(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that the correct API endpoint is called."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        requirement_yogi_client.get_requirement("TYS", "AR_ANSL_001")

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["method"] == "GET"
        assert "/requirement2/TYS/AR_ANSL_001" in call_args.kwargs["url"]

    def test_get_requirement_with_preprocessing(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that preprocessor is applied to requirement content."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        result = requirement_yogi_client.get_requirement("TYS", "AR_ANSL_001")

        # Storage data should be present
        assert result.storage_data is not None

    def test_get_requirement_with_properties(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that properties are parsed from API response."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        result = requirement_yogi_client.get_requirement("TYS", "AR_ANSL_001")

        assert len(result.properties) == 3
        assert result.get_property("Category") == "Functional"
        assert result.get_property("Priority") == "High"

    def test_get_requirement_with_references(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that references are parsed from API response."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        result = requirement_yogi_client.get_requirement("TYS", "AR_ANSL_001")

        assert len(result.references) == 2
        assert result.references[0].key == "AS_017"

    def test_get_requirement_with_jira_links(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that JIRA links are parsed from API response."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        result = requirement_yogi_client.get_requirement("TYS", "AR_ANSL_001")

        assert len(result.jira_links) == 1
        assert result.jira_links[0].issue_key == "OCX-11076"

    def test_get_requirement_spaces_filter_allowed(
        self, requirement_yogi_client_with_filter, mock_ry_session
    ):
        """Test that allowed spaces pass the filter."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        # TYS is in the filter (TYS,OCX,DEV)
        result = requirement_yogi_client_with_filter.get_requirement(
            "TYS", "AR_ANSL_001"
        )
        assert isinstance(result, Requirement)

    def test_get_requirement_spaces_filter_rejected(
        self, requirement_yogi_client_with_filter
    ):
        """Test that disallowed spaces are rejected by filter."""
        with pytest.raises(ValueError, match="not in the allowed spaces filter"):
            requirement_yogi_client_with_filter.get_requirement(
                "BLOCKED", "REQ-001"
            )

    def test_get_requirement_auth_error(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test handling of authentication errors."""
        mock_response = mock_ry_session.request.return_value
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with pytest.raises(MCPAtlassianAuthenticationError):
            requirement_yogi_client.get_requirement("TYS", "AR_ANSL_001")


class TestListRequirements:
    """Tests for RequirementsMixin.list_requirements()."""

    def test_list_requirements_returns_model(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that list_requirements returns a RequirementSearchResult."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_SEARCH_RESPONSE

        result = requirement_yogi_client.list_requirements("TYS")

        assert isinstance(result, RequirementSearchResult)
        assert result.count == 50
        assert len(result.results) == 3

    def test_list_requirements_api_endpoint(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that the correct API endpoint is called."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_SEARCH_RESPONSE

        requirement_yogi_client.list_requirements("TYS", limit=25)

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["method"] == "GET"
        assert "/requirement2/TYS" in call_args.kwargs["url"]
        assert call_args.kwargs["params"]["limit"] == 25

    def test_list_requirements_with_query(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test listing requirements with a search query."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_SEARCH_RESPONSE

        result = requirement_yogi_client.list_requirements(
            "TYS", query="key ~ 'AS_%'"
        )

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["params"]["q"] == "key ~ 'AS_%'"
        assert isinstance(result, RequirementSearchResult)

    def test_list_requirements_invalid_limit_low(
        self, requirement_yogi_client
    ):
        """Test that limit < 1 raises ValueError."""
        with pytest.raises(ValueError, match="Limit must be between"):
            requirement_yogi_client.list_requirements("TYS", limit=0)

    def test_list_requirements_invalid_limit_high(
        self, requirement_yogi_client
    ):
        """Test that limit > MAX raises ValueError."""
        with pytest.raises(ValueError, match="Limit must be between"):
            requirement_yogi_client.list_requirements(
                "TYS", limit=MAX_REQUIREMENTS_LIMIT + 1
            )

    def test_list_requirements_valid_limits(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that valid limits are accepted."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_SEARCH_RESPONSE

        # Min valid
        result = requirement_yogi_client.list_requirements("TYS", limit=1)
        assert isinstance(result, RequirementSearchResult)

        # Max valid
        result = requirement_yogi_client.list_requirements(
            "TYS", limit=MAX_REQUIREMENTS_LIMIT
        )
        assert isinstance(result, RequirementSearchResult)

    def test_list_requirements_spaces_filter(
        self, requirement_yogi_client_with_filter
    ):
        """Test that spaces filter is applied to list_requirements."""
        with pytest.raises(ValueError, match="not in the allowed spaces filter"):
            requirement_yogi_client_with_filter.list_requirements("BLOCKED")


class TestCreateRequirement:
    """Tests for RequirementsMixin.create_requirement()."""

    def test_create_requirement_returns_model(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that create_requirement returns a Requirement model."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_CREATE_RESPONSE

        result = requirement_yogi_client.create_requirement(
            "DEV", "REQ-NEW-001", {"title": "New Requirement"}
        )

        assert isinstance(result, Requirement)
        assert result.key == "REQ-NEW-001"

    def test_create_requirement_api_call(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that POST is made with correct data."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_CREATE_RESPONSE

        data = {"title": "New Requirement", "description": "Test description"}
        requirement_yogi_client.create_requirement("DEV", "REQ-NEW-001", data)

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "/requirement2/DEV/REQ-NEW-001" in call_args.kwargs["url"]
        assert call_args.kwargs["json"] == data

    def test_create_requirement_missing_title(
        self, requirement_yogi_client
    ):
        """Test that missing title raises ValueError."""
        with pytest.raises(ValueError, match="title"):
            requirement_yogi_client.create_requirement(
                "DEV", "REQ-001", {"description": "No title"}
            )

    def test_create_requirement_empty_data(
        self, requirement_yogi_client
    ):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError):
            requirement_yogi_client.create_requirement("DEV", "REQ-001", {})


class TestUpdateRequirement:
    """Tests for RequirementsMixin.update_requirement()."""

    def test_update_requirement_returns_model(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that update_requirement returns a Requirement model."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_UPDATE_RESPONSE

        result = requirement_yogi_client.update_requirement(
            "TYS", "AR_ANSL_001", {"title": "Updated Title"}
        )

        assert isinstance(result, Requirement)

    def test_update_requirement_api_call(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that PUT is made with correct data."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_UPDATE_RESPONSE

        data = {"title": "Updated Title"}
        requirement_yogi_client.update_requirement("TYS", "AR_ANSL_001", data)

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["method"] == "PUT"
        assert "/requirement2/TYS/AR_ANSL_001" in call_args.kwargs["url"]


class TestDeleteRequirement:
    """Tests for RequirementsMixin.delete_requirement()."""

    def test_delete_requirement_returns_dict(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that delete_requirement returns a dict."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = {}

        result = requirement_yogi_client.delete_requirement("TYS", "AR_ANSL_001")

        assert isinstance(result, dict)

    def test_delete_requirement_api_call(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that DELETE is made to correct endpoint."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = {}

        requirement_yogi_client.delete_requirement("TYS", "AR_ANSL_001")

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["method"] == "DELETE"
        assert "/requirement2/TYS/AR_ANSL_001" in call_args.kwargs["url"]

    def test_delete_requirement_empty_response(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test handling of empty response from delete."""
        mock_response = mock_ry_session.request.return_value
        mock_response.content = b""
        mock_response.json.side_effect = Exception("No content")
        # Simulate empty response
        mock_response.content = None

        # The _request method returns None for empty content
        # delete_requirement should handle this gracefully
        # We need to make content truthy to enter json parsing or falsy to return None
        mock_response.content = b""

        result = requirement_yogi_client.delete_requirement("TYS", "AR_ANSL_001")
        assert isinstance(result, dict)


class TestBulkUpdateRequirements:
    """Tests for RequirementsMixin.bulk_update_requirements()."""

    def test_bulk_update_returns_dict(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that bulk_update returns a dict."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = {"updated": 2, "failed": 0}

        result = requirement_yogi_client.bulk_update_requirements(
            "TYS",
            [
                {"key": "REQ-001", "title": "Updated 1"},
                {"key": "REQ-002", "title": "Updated 2"},
            ],
        )

        assert isinstance(result, dict)
        assert result["updated"] == 2

    def test_bulk_update_empty_list(self, requirement_yogi_client):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            requirement_yogi_client.bulk_update_requirements("TYS", [])

    def test_bulk_update_api_call(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that PUT is made to space endpoint."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = {"updated": 1, "failed": 0}

        data = [{"key": "REQ-001", "title": "Updated"}]
        requirement_yogi_client.bulk_update_requirements("TYS", data)

        call_args = mock_ry_session.request.call_args
        assert call_args.kwargs["method"] == "PUT"
        assert "/requirement2/TYS" in call_args.kwargs["url"]
        assert call_args.kwargs["json"] == {"requirements": data}


class TestSpacesFilter:
    """Tests for space filter functionality across all methods."""

    def test_filter_allows_configured_spaces(
        self, requirement_yogi_client_with_filter, mock_ry_session
    ):
        """Test that configured spaces are allowed through filter."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        # TYS, OCX, DEV are all in the filter
        for space in ["TYS", "OCX", "DEV"]:
            result = requirement_yogi_client_with_filter.get_requirement(
                space, "REQ-001"
            )
            assert isinstance(result, Requirement)

    def test_filter_blocks_unconfigured_spaces(
        self, requirement_yogi_client_with_filter
    ):
        """Test that unconfigured spaces are blocked."""
        for space in ["BLOCKED", "OTHER", "RANDOM"]:
            with pytest.raises(ValueError, match="not in the allowed spaces"):
                requirement_yogi_client_with_filter.get_requirement(
                    space, "REQ-001"
                )

    def test_no_filter_allows_all_spaces(
        self, requirement_yogi_client, mock_ry_session
    ):
        """Test that without filter, all spaces are allowed."""
        mock_response = mock_ry_session.request.return_value
        mock_response.json.return_value = MOCK_REQUIREMENT_RESPONSE

        for space in ["ANY", "SPACE", "WORKS"]:
            result = requirement_yogi_client.get_requirement(space, "REQ-001")
            assert isinstance(result, Requirement)
