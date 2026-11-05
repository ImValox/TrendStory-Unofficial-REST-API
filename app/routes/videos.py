"""
Video generation and management routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from trendstory.client import TrendStoryClient, TrendStoryApiError, TrendStoryAuthError
from trendstory.models import ApiResponse, GenerateVideoRequest

router = APIRouter(prefix="/videos", tags=["Vidéos & Génération"])


def get_client() -> TrendStoryClient:
    return TrendStoryClient(session_file="session.json")


@router.get("", response_model=ApiResponse)
async def list_videos(client: TrendStoryClient = Depends(get_client)):
    """
    Récupère la liste de toutes vos vidéos générées (historique des créations).
    """
    try:
        videos = await client.list_videos()
        return ApiResponse(success=True, data=videos)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/pending", response_model=ApiResponse)
async def list_pending_videos(client: TrendStoryClient = Depends(get_client)):
    """
    Récupère la liste des vidéos actuellement en cours de génération.
    """
    try:
        pendings = await client.list_pending_videos()
        return ApiResponse(success=True, data=pendings)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/generate", response_model=ApiResponse)
async def generate_video(
    req: GenerateVideoRequest,
    client: TrendStoryClient = Depends(get_client),
):
    """
    Lance la génération d'une nouvelle vidéo IA complète à partir d'un prompt.
    Génère le script, la voix off, les images cohérentes et les sous-titres animés.
    """
    try:
        res = await client.generate_video(
            prompt=req.prompt,
            style=req.style,
            video_model=req.video_model or "kling-v1",
            video_tier=req.video_tier or "standard",
            image_model=req.image_model or "nano-banana",
            duration_option=req.duration_option or "30s",
            subtitle_style=req.subtitle_style or "trend",
            music_source=req.music_source or "library",
            music_id=req.music_id,
            locale=req.locale or "fr",
            series_id=req.series_id,
        )
        return ApiResponse(success=True, data=res)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        # Note: if credits are 0, this returns VIDEO_LOCKED (403)
        raise HTTPException(
            status_code=e.status_code,
            detail=f"{str(e)} (Vérifiez si votre compte a des crédits disponibles)"
        )


@router.get("/{video_id}", response_model=ApiResponse)
async def get_video(video_id: str, client: TrendStoryClient = Depends(get_client)):
    """
    Récupère les détails, le statut et les métadonnées d'une vidéo spécifique.
    """
    try:
        video = await client.get_video(video_id)
        return ApiResponse(success=True, data=video)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/{video_id}/download-url", response_model=ApiResponse)
async def get_video_download_url(video_id: str, client: TrendStoryClient = Depends(get_client)):
    """
    Récupère l'URL de téléchargement direct (MP4 signé Cloudflare/R2) de la vidéo finale.
    """
    try:
        data = await client.get_video_download_url(video_id)
        return ApiResponse(success=True, data=data)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/{video_id}/cancel", response_model=ApiResponse)
async def cancel_video(video_id: str, client: TrendStoryClient = Depends(get_client)):
    """
    Annule une génération de vidéo en cours.
    """
    try:
        res = await client.cancel_video(video_id)
        return ApiResponse(success=True, data=res)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

