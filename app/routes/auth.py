"""
Authentication routes for TrendStory microservice.
"""

from fastapi import APIRouter, HTTPException, Depends
from trendstory.client import TrendStoryClient, TrendStoryAuthError
from trendstory.models import LoginRequest, RefreshTokenRequest, SetSessionRequest, ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentification"])


def get_client() -> TrendStoryClient:
    return TrendStoryClient()


@router.post("/session", response_model=ApiResponse)
async def set_session(
    req: SetSessionRequest,
    client: TrendStoryClient = Depends(get_client),
):
    """
    Définit manuellement une nouvelle session Supabase (access_token + refresh_token).
    Valide les jetons en direct avec Supabase, récupère le profil utilisateur et enregistre dans session.json.
    """
    try:
        data = await client.set_session(
            access_token=req.access_token,
            refresh_token=req.refresh_token,
        )
        return ApiResponse(
            success=True,
            data={
                "message": "Session mise à jour et validée avec succès",
                "email": data.get("email"),
                "expires_at": data.get("expires_at"),
            },
        )
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/login", response_model=ApiResponse)
async def login(req: LoginRequest, client: TrendStoryClient = Depends(get_client)):
    """
    Connecte l'utilisateur avec son email et mot de passe.
    Si Cloudflare Turnstile est actif sur le domaine, un `captcha_token` peut être fourni.
    """
    try:
        data = await client.login(
            email=req.email,
            password=req.password,
            captcha_token=req.captcha_token,
        )
        return ApiResponse(
            success=True,
            data={
                "message": "Connexion réussie",
                "email": data.get("user", {}).get("email"),
                "expires_at": data.get("expires_at"),
            },
        )
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(
    req: RefreshTokenRequest = RefreshTokenRequest(),
    client: TrendStoryClient = Depends(get_client),
):
    """
    Renouvelle le jeton d'accès (access_token) via le refresh_token Supabase.
    Cette méthode ne requiert aucun captcha et renouvelle automatiquement la session.
    """
    try:
        data = await client.refresh_session(refresh_tok=req.refresh_token)
        return ApiResponse(
            success=True,
            data={
                "message": "Token renouvelé avec succès",
                "expires_at": data.get("expires_at"),
                "email": data.get("user", {}).get("email"),
            },
        )
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/status", response_model=ApiResponse)
async def get_auth_status(client: TrendStoryClient = Depends(get_client)):
    """
    Indique si le client dispose d'une session active valide.
    """
    is_auth = client.is_authenticated()
    user_email = client.user.get("email") if client.user else None
    return ApiResponse(
        success=True,
        data={
            "authenticated": is_auth,
            "email": user_email,
            "expires_at": client.expires_at,
        },
    )

