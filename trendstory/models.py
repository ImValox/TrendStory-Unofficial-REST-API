"""
Pydantic models for TrendStory API requests and responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(..., description="Email de connexion TrendStory")
    password: str = Field(..., description="Mot de passe du compte")
    captcha_token: Optional[str] = Field(
        None,
        description="Token captcha Cloudflare Turnstile si requis lors du premier login"
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = Field(
        None,
        description="Refresh token Supabase. Si non renseigné, la session active sera utilisée."
    )


class SetSessionRequest(BaseModel):
    access_token: str = Field(..., description="Access token JWT Supabase")
    refresh_token: str = Field(..., description="Refresh token Supabase")


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="Sujet ou script de la vidéo à générer (ex: 'Histoire fascinante sur les abysses sous-marins')"
    )
    style: str = Field(
        default="human-pixar",
        description="Style visuel (ex: human-pixar, fruit, animals-3d, realistic, etc.)"
    )
    video_model: Optional[str] = Field(
        default="kling-v1",
        description="Modèle vidéo (ex: kling-v1, luma-ray, grok-imagine, etc.)"
    )
    video_tier: Optional[str] = Field(
        default="normal",
        description="Tier de rendu vidéo (normal, lite)"
    )
    image_model: Optional[str] = Field(
        default="nano-banana",
        description="Modèle d'image utilisé pour les scènes (ex: nano-banana, grok-imagine, flux-schnell)"
    )
    duration_option: Optional[str] = Field(
        default="30s",
        description="Durée cible de la vidéo (ex: 30s, 60s, 90s)"
    )
    subtitle_style: Optional[str] = Field(
        default="karaoke",
        description="Style des sous-titres animés (karaoke, simple, italic)"
    )
    music_source: Optional[str] = Field(
        default="library",
        description="Source musicale (library, user, none)"
    )
    music_id: Optional[str] = Field(
        default="track-6",
        description="ID du morceau de musique choisi (ex: track-6)"
    )
    locale: Optional[str] = Field(
        default="fr",
        description="Langue de narration et du script (fr, en, es, etc.)"
    )
    series_id: Optional[str] = Field(
        default=None,
        description="Optionnel: ID d'une série associée"
    )


class FastVideoToolRequest(BaseModel):
    prompt: str = Field(..., description="Prompt texte pour la génération vidéo directe")
    model: Optional[str] = Field(default="kling-v1", description="Modèle vidéo")
    aspect_ratio: Optional[str] = Field(default="9:16", description="Format d'image (9:16 pour vertical/TikTok)")
    outputs: Optional[int] = Field(default=1, description="Nombre de variantes")
    locale: Optional[str] = Field(default="fr", description="Langue")


class CreateStudioProjectRequest(BaseModel):
    name: str = Field(..., description="Nom du projet studio")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: Optional[int] = None
    refresh_token: str
    user: Dict[str, Any]


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None

