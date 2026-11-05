"""
TrendStory Unofficial API SDK and Gateway.
"""

from trendstory.client import TrendStoryClient, TrendStoryAuthError, TrendStoryApiError
from trendstory.models import (
    LoginRequest,
    RefreshTokenRequest,
    GenerateVideoRequest,
    FastVideoToolRequest,
    CreateStudioProjectRequest,
)

__all__ = [
    "TrendStoryClient",
    "TrendStoryAuthError",
    "TrendStoryApiError",
    "LoginRequest",
    "RefreshTokenRequest",
    "GenerateVideoRequest",
    "FastVideoToolRequest",
    "CreateStudioProjectRequest",
]

