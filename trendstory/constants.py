"""
Constants for TrendStory API Gateway.
"""

SUPABASE_AUTH_URL = "https://tvzwvkiaahukacteompc.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_bqbe1ZehMQQ7Jl_A2gYLrw_PEY7idZP"
BACKEND_API_BASE = "https://api-trendstory-production.up.railway.app"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
)

# Standard video styles observed in TrendStory
VIDEO_STYLES = [
    "hyperrealistic",
    "anime",
    "cinematic",
    "comic",
    "3d-render",
    "cyberpunk",
    "retro",
    "fantasy",
    "minimalist",
]

# Standard models
IMAGE_MODELS = [
    "nano-banana",
    "grok-imagine",
    "flux-schnell",
    "flux-dev",
]

VIDEO_MODELS = [
    "kling-v1",
    "luma-ray",
    "runway-gen3",
]

