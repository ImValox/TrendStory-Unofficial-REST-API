"""
Studio and creative tools routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from trendstory.client import TrendStoryClient, TrendStoryApiError, TrendStoryAuthError
from trendstory.models import (
    ApiResponse,
    CreateStudioProjectRequest,
    FastVideoToolRequest,
)

router = APIRouter(prefix="/studio", tags=["Studio & Outils"])


def get_client() -> TrendStoryClient:
    return TrendStoryClient()


@router.get("/projects", response_model=ApiResponse)
async def list_studio_projects(client: TrendStoryClient = Depends(get_client)):
    """
    Récupère la liste de tous vos projets Studio.
    """
    try:
        projects = await client.list_studio_projects()
        return ApiResponse(success=True, data=projects)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/projects", response_model=ApiResponse)
async def create_studio_project(
    req: CreateStudioProjectRequest,
    client: TrendStoryClient = Depends(get_client),
):
    """
    Crée un nouveau projet dans le Studio TrendStory.
    """
    try:
        project = await client.create_studio_project(name=req.name)
        return ApiResponse(success=True, data=project)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/projects/{project_id}", response_model=ApiResponse)
async def get_studio_project(project_id: str, client: TrendStoryClient = Depends(get_client)):
    """
    Récupère les détails d'un projet Studio, incluant ses scènes et ses clips.
    """
    try:
        project = await client.get_studio_project(project_id)
        return ApiResponse(success=True, data=project)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/models", response_model=ApiResponse)
async def list_models(client: TrendStoryClient = Depends(get_client)):
    """
    Récupère les modèles d'IA disponibles (images et vidéos) avec leurs coûts en crédits.
    """
    try:
        models = await client.list_studio_models()
        return ApiResponse(success=True, data=models)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/fast-video", response_model=ApiResponse)
async def generate_fast_video(
    req: FastVideoToolRequest,
    client: TrendStoryClient = Depends(get_client),
):
    """
    Génère directement un clip vidéo via l'outil rapide (tools/video).
    """
    try:
        res = await client.generate_fast_video(
            prompt=req.prompt,
            model=req.model or "kling-v1",
            aspect_ratio=req.aspect_ratio or "9:16",
            outputs=req.outputs or 1,
            locale=req.locale or "fr",
        )
        return ApiResponse(success=True, data=res)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/characters", response_model=ApiResponse)
async def list_characters(client: TrendStoryClient = Depends(get_client)):
    """
    Liste les personnages personnalisés créés sur le compte.
    """
    try:
        characters = await client.list_characters()
        return ApiResponse(success=True, data=characters)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/character-presets", response_model=ApiResponse)
async def list_character_presets(client: TrendStoryClient = Depends(get_client)):
    """
    Liste les modèles de personnages prédéfinis de TrendStory (ex: Fraisita, etc.).
    """
    try:
        presets = await client.list_character_presets()
        return ApiResponse(success=True, data=presets)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/music", response_model=ApiResponse)
async def list_music(client: TrendStoryClient = Depends(get_client)):
    """
    Liste les musiques de fond de la librairie TrendStory.
    """
    try:
        music = await client.list_music_library()
        return ApiResponse(success=True, data=music)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

