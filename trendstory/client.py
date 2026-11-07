"""
TrendStory API Client.
Handles Supabase token management, auto-refresh, and Railway backend API endpoints.
"""

import base64
import json
import os
import time
from typing import Any, Dict, List, Optional
import httpx

from trendstory.constants import (
    BACKEND_API_BASE,
    DEFAULT_USER_AGENT,
    SUPABASE_ANON_KEY,
    SUPABASE_AUTH_URL,
)


class TrendStoryAuthError(Exception):
    """Raised when authentication or token refresh fails."""
    pass


class TrendStoryApiError(Exception):
    """Raised when the TrendStory backend API returns an error."""
    def __init__(self, message: str, status_code: int = 500, response_data: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


def extract_jwt_exp(token: Optional[str]) -> Optional[int]:
    """Extracts expiration timestamp (exp) from a JWT without signature verification."""
    if not token or not isinstance(token, str):
        return None
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            padding = "=" * ((4 - len(parts[1]) % 4) % 4)
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + padding))
            return payload.get("exp")
    except Exception:
        pass
    return None


DEFAULT_SESSION_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session.json"
)


class TrendStoryClient:
    def __init__(
        self,
        session_file: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        auto_load: bool = True,
    ):
        self.session_file = session_file or os.getenv("SESSION_FILE") or DEFAULT_SESSION_FILE
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at: Optional[int] = None
        self.user: Optional[Dict[str, Any]] = None

        env_access = os.getenv("TRENDSTORY_ACCESS_TOKEN")
        env_refresh = os.getenv("TRENDSTORY_REFRESH_TOKEN")

        # Load session from session.json first
        if auto_load and not self.access_token:
            self.load_session()

        # If .env has refresh_token, use it if not already present
        if env_refresh and not self.refresh_token:
            self.refresh_token = env_refresh

        # If we still have no access token, fallback to .env access token
        if not self.access_token and env_access:
            self.access_token = env_access
            self.expires_at = extract_jwt_exp(env_access)

        # Always ensure expires_at is set if access_token is present
        if self.access_token and not self.expires_at:
            self.expires_at = extract_jwt_exp(self.access_token)

    def load_session(self) -> bool:
        """Loads saved session from local JSON file."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.expires_at = data.get("expires_at") or extract_jwt_exp(self.access_token)
                    self.user = data.get("user")
                    return True
            except Exception:
                return False
        return False

    def save_session(self) -> None:
        """Saves current tokens and user info to session file."""
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "access_token": self.access_token,
                        "refresh_token": self.refresh_token,
                        "expires_at": self.expires_at,
                        "user": self.user,
                        "updated_at": int(time.time()),
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"[Warning] Could not save session to {self.session_file}: {e}")

    def is_authenticated(self) -> bool:
        """Check whether we have an active access token or a refresh token."""
        return bool(self.access_token or self.refresh_token)

    async def login(
        self,
        email: str,
        password: str,
        captcha_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Authenticate with Supabase using email + password (and optional Cloudflare captcha token).
        """
        url = f"{SUPABASE_AUTH_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
        }
        payload: Dict[str, Any] = {
            "email": email,
            "password": password,
        }
        if captcha_token:
            payload["gotrue_meta_security"] = {"captcha_token": captcha_token}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise TrendStoryAuthError(
                    f"Login failed ({resp.status_code}): {resp.text}"
                )

            data = resp.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            self.expires_at = data.get("expires_at") or int(
                time.time() + data.get("expires_in", 3600)
            )
            self.user = data.get("user")
            self.save_session()
            return data

    async def refresh_session(
        self, refresh_tok: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refreshes access token with Supabase using refresh_token.
        Does NOT require any captcha!
        """
        tok = refresh_tok or self.refresh_token
        if not tok:
            raise TrendStoryAuthError("No refresh token available to refresh session.")

        url = f"{SUPABASE_AUTH_URL}/auth/v1/token?grant_type=refresh_token"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
        }
        payload = {"refresh_token": tok}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise TrendStoryAuthError(
                    f"Token refresh failed ({resp.status_code}): {resp.text}"
                )

            data = resp.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            self.expires_at = data.get("expires_at") or int(
                time.time() + data.get("expires_in", 3600)
            )
            self.user = data.get("user")
            self.save_session()
            return data

    async def set_session(
        self, access_token: str, refresh_token: str
    ) -> Dict[str, Any]:
        """Sets new session tokens, saves them to file immediately, and validates them."""
        self.access_token = access_token.strip()
        self.refresh_token = refresh_token.strip()
        self.expires_at = extract_jwt_exp(self.access_token)
        self.save_session()

        # Validate tokens by calling get_me
        try:
            profile = await self.get_me()
            self.user = profile
            self.save_session()
            return {
                "email": profile.get("email"),
                "expires_at": self.expires_at,
                "user": profile,
            }
        except Exception as e:
            # If access_token was already expired, attempt immediate refresh
            try:
                data = await self.refresh_session()
                return {
                    "email": self.user.get("email") if self.user else None,
                    "expires_at": self.expires_at,
                    "user": self.user,
                }
            except Exception as ref_err:
                raise TrendStoryAuthError(
                    f"Tokens invalides : {e} (Tentative de refresh échouée: {ref_err})"
                )

    async def _ensure_token(self) -> str:
        """Ensures access token is present and not expired."""
        if not self.access_token:
            self.load_session()

        if not self.access_token and self.refresh_token:
            await self.refresh_session()

        if self.access_token and not self.expires_at:
            self.expires_at = extract_jwt_exp(self.access_token)

        # Check expiration (with 120-second buffer)
        is_expired = bool(self.expires_at and time.time() > (self.expires_at - 120))
        if is_expired and self.refresh_token:
            try:
                await self.refresh_session()
            except Exception as e:
                print(f"[Warning] Auto-refresh in _ensure_token failed: {e}")

        if not self.access_token:
            raise TrendStoryAuthError("Client is not authenticated. Please login or provide a valid token.")

        return self.access_token

    async def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_on_401: bool = True,
    ) -> Any:
        """
        Executes an authenticated HTTP request against TrendStory backend API.
        Automatically retries on 401 by refreshing the token.
        """
        token = await self._ensure_token()

        url = path if path.startswith("http") else f"{BACKEND_API_BASE}{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )

            # If 401 Unauthorized, reload session and attempt refresh once
            if resp.status_code == 401 and retry_on_401:
                self.load_session()
                if self.refresh_token:
                    try:
                        await self.refresh_session()
                        return await self.request(
                            method=method,
                            path=path,
                            json_data=json_data,
                            params=params,
                            retry_on_401=False,
                        )
                    except Exception as e:
                        print(f"[Warning] Auto-refresh on 401 failed: {e}")

            if resp.status_code >= 400:
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("error") or err_json.get("message") or resp.text
                except Exception:
                    err_json = None
                    err_msg = resp.text
                raise TrendStoryApiError(
                    f"TrendStory API error ({resp.status_code}): {err_msg}",
                    status_code=resp.status_code,
                    response_data=err_json,
                )

            try:
                return resp.json()
            except Exception:
                return resp.text

    # --- Profile & Credits ---

    async def get_me(self) -> Dict[str, Any]:
        """Returns the current user profile, email, plan, and credit balance."""
        res = await self.request("GET", "/api/me")
        return res.get("data", res)

    async def get_credits(self) -> Dict[str, Any]:
        """Returns detailed credits balance (plan credits, topup credits, total)."""
        res = await self.request("GET", "/api/credits/balance")
        return res.get("data", res)

    # --- Videos ---

    async def list_videos(self) -> List[Dict[str, Any]]:
        """Returns the list of generated videos."""
        res = await self.request("GET", "/api/videos")
        return res.get("data", res)

    async def list_pending_videos(self) -> List[Dict[str, Any]]:
        """Returns the list of videos currently generating / pending."""
        res = await self.request("GET", "/api/videos/pending")
        if isinstance(res, dict) and "data" in res:
            return res["data"].get("pendings", [])
        return res

    async def get_video(self, video_id: str) -> Dict[str, Any]:
        """Returns details, status and metadata of a specific video."""
        res = await self.request("GET", f"/api/videos/{video_id}")
        return res.get("data", res)

    async def get_video_download_url(self, video_id: str) -> Dict[str, Any]:
        """Returns the signed direct download URL (MP4) for a video."""
        res = await self.request("GET", f"/api/videos/{video_id}/download-url")
        return res.get("data", res)

    async def cancel_video(self, video_id: str) -> Dict[str, Any]:
        """Cancels an in-progress video generation."""
        return await self.request("POST", f"/api/videos/{video_id}/cancel")

    async def generate_video_clips(self, video_id: str) -> Dict[str, Any]:
        """
        Triggers Phase 2: turns generated scenes/images into animated clips and final video MP4.
        Call this when the video reaches status 'preview_ready'.
        """
        return await self.request("POST", f"/api/videos/{video_id}/generate-videos")

    async def generate_video(
        self,
        prompt: str,
        style: str = "cinematic",
        video_model: str = "kling-v1",
        video_tier: str = "standard",
        image_model: str = "nano-banana",
        duration_option: str = "30s",
        subtitle_style: str = "trend",
        music_source: str = "library",
        music_id: Optional[str] = None,
        locale: str = "fr",
        series_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Triggers a full AI short video generation (script, voiceover, images, clips, subtitles).
        """
        payload = {
            "prompt": prompt,
            "style": style,
            "video_model": video_model,
            "video_tier": video_tier,
            "image_model": image_model,
            "duration_option": duration_option,
            "subtitle_style": subtitle_style,
            "music_source": music_source,
            "music_id": music_id,
            "locale": locale,
        }
        if series_id:
            payload["series_id"] = series_id

        res = await self.request("POST", "/api/videos/generate", json_data=payload)
        return res

    # --- Studio Projects ---

    async def list_studio_projects(self) -> List[Dict[str, Any]]:
        """Returns user's Studio projects."""
        res = await self.request("GET", "/api/studio/projects")
        if isinstance(res, dict) and "data" in res:
            return res["data"].get("projects", [])
        return res

    async def get_studio_project(self, project_id: str) -> Dict[str, Any]:
        """Returns a studio project and its scenes."""
        res = await self.request("GET", f"/api/studio/projects/{project_id}")
        return res.get("data", res)

    async def create_studio_project(self, name: str) -> Dict[str, Any]:
        """Creates a new Studio project."""
        res = await self.request("POST", "/api/studio/projects", json_data={"name": name})
        return res.get("data", res)

    async def list_studio_models(self) -> Dict[str, Any]:
        """Returns available studio image/video models and their credit costs."""
        res = await self.request("GET", "/api/studio/models")
        return res.get("data", res)

    # --- Fast Video Tool ---

    async def generate_fast_video(
        self,
        prompt: str,
        model: str = "kling-v1",
        aspect_ratio: str = "9:16",
        outputs: int = 1,
        locale: str = "fr",
    ) -> Dict[str, Any]:
        """Generates a direct AI video clip using the tools API."""
        payload = {
            "prompt": prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "outputs": outputs,
            "locale": locale,
        }
        return await self.request("POST", "/api/tools/video", json_data=payload)

    # --- Music & Characters ---

    async def list_music_library(self) -> List[Dict[str, Any]]:
        """Returns available music tracks for background audio."""
        res = await self.request("GET", "/api/music/library")
        return res.get("data", res)

    async def list_characters(self) -> List[Dict[str, Any]]:
        """Returns custom created characters."""
        res = await self.request("GET", "/api/characters")
        if isinstance(res, dict) and "data" in res:
            return res["data"].get("characters", [])
        return res

    async def list_character_presets(self) -> List[Dict[str, Any]]:
        """Returns presets for consistent characters (e.g. Fraisita, etc.)."""
        res = await self.request("GET", "/api/characters/presets")
        if isinstance(res, dict) and "data" in res:
            return res["data"].get("presets", [])
        return res

