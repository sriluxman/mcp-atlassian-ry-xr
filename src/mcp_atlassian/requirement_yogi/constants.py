"""Constants for Requirements Yogi API."""

# Base API path
API_BASE_PATH = "/rest/reqs/1"

# API version
API_VERSION = "1"

# Default limits
DEFAULT_REQUIREMENTS_LIMIT = 50
MAX_REQUIREMENTS_LIMIT = 200

# Endpoints (relative to API_BASE_PATH)
ENDPOINTS = {
    # RequirementResource2 (Public API)
    "get_requirement": "/requirement2/{spaceKey}/{key}",
    "list_requirements": "/requirement2/{spaceKey}",
    "create_requirement": "/requirement2/{spaceKey}/{key}",
    "update_requirement": "/requirement2/{spaceKey}/{key}",
    "delete_requirement": "/requirement2/{spaceKey}/{key}",
    "bulk_update_requirements": "/requirement2/{spaceKey}",
    # RequirementResource3 (Bulk operations)
    "bulk_get_requirements": "/requirement3/request",
    # BaselineResource (Public API)
    "list_baselines": "/baseline/{spaceKey}",
    "get_baseline": "/baseline/{spaceKey}/{version}",
    "get_baseline_pages": "/baseline/{spaceKey}/{version}/pages",
    "create_baseline": "/baseline/{spaceKey}",
    "update_baseline": "/baseline/{spaceKey}/{version}",
    "update_baseline_label": "/baseline/{spaceKey}/{version}/label",
    "delete_baseline": "/baseline/{spaceKey}/{version}",
}

# HTTP Methods
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"
