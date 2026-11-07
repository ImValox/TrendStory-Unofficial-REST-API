"""
Buffer publishing routes for TrendStory microservice.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from trendstory.buffer import BufferClient, BufferApiError
from trendstory.client import TrendStoryClient, TrendStoryApiError, TrendStoryAuthError
from trendstory.models import ApiResponse

router = APIRouter(prefix="/buffer", tags=["Publication Buffer (TikTok)"])


class PublishToBufferRequest(BaseModel):
    channel_id: str = Field(
        ...,
        description="ID du compte TikTok sur Buffer (obtenez-le via GET /buffer/channels)",
    )
    text: str = Field(
        ...,
        description="Description de la vidéo TikTok et hashtags (ex: 'Top 5 faits insolites #pourtoi #fyp')",
    )
    video_id: Optional[str] = Field(
        None,
        description="ID d'une vidéo TrendStory (l'URL de téléchargement sera récupérée automatiquement)",
    )
    video_url: Optional[str] = Field(
        None,
        description="Ou directement l'URL publique/signée du fichier MP4",
    )
    post_now: bool = Field(
        default=True,
        description="Publier immédiatement (True) ou ajouter à la file d'attente Buffer (False)",
    )


def get_buffer_client() -> BufferClient:
    return BufferClient()


def get_trendstory_client() -> TrendStoryClient:
    return TrendStoryClient(session_file="session.json")


@router.get("/channels", response_model=ApiResponse)
async def list_buffer_channels(
    buffer_client: BufferClient = Depends(get_buffer_client),
):
    """
    Récupère la liste de vos comptes connectés sur Buffer (vos comptes TikTok, Instagram, etc.) avec leurs IDs.
    """
    try:
        channels = await buffer_client.get_channels()
        return ApiResponse(success=True, data=channels)
    except BufferApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/publish", response_model=ApiResponse)
async def publish_to_buffer(
    req: PublishToBufferRequest,
    buffer_client: BufferClient = Depends(get_buffer_client),
    ts: TrendStoryClient = Depends(get_trendstory_client),
):
    """
    Publie automatiquement une vidéo TrendStory sur un compte TikTok via Buffer.
    Fournissez soit `video_id` (ID TrendStory), soit `video_url` (URL MP4 directe).
    """
    video_url = req.video_url

    # Si un video_id TrendStory est fourni, récupérer l'URL de téléchargement signée
    if req.video_id:
        try:
            dl_info = await ts.get_video_download_url(req.video_id)
            video_url = (
                dl_info.get("download_url")
                or dl_info.get("url")
                or (dl_info if isinstance(dl_info, str) else None)
            )
        except (TrendStoryAuthError, TrendStoryApiError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de récupérer l'URL de la vidéo TrendStory: {str(e)}",
            )

    if not video_url:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier soit 'video_id' (TrendStory), soit 'video_url' directe.",
        )

    try:
        result = await buffer_client.publish_video(
            channel_id=req.channel_id,
            video_url=video_url,
            text=req.text,
            post_now=req.post_now,
        )
        return ApiResponse(success=True, data=result)
    except BufferApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

