"""
Account and credits routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from trendstory.client import TrendStoryClient, TrendStoryApiError, TrendStoryAuthError
from trendstory.models import ApiResponse

router = APIRouter(prefix="/account", tags=["Compte & Crédits"])


def get_client() -> TrendStoryClient:
    return TrendStoryClient()


@router.get("/me", response_model=ApiResponse)
async def get_my_profile(client: TrendStoryClient = Depends(get_client)):
    """
    Récupère le profil du compte TrendStory (ID, email, crédits, plan actif).
    """
    try:
        profile = await client.get_me()
        return ApiResponse(success=True, data=profile)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/credits", response_model=ApiResponse)
async def get_credits_balance(client: TrendStoryClient = Depends(get_client)):
    """
    Récupère le solde détaillé des crédits (plan_credits, topup_credits, total).
    """
    try:
        balance = await client.get_credits()
        return ApiResponse(success=True, data=balance)
    except TrendStoryAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TrendStoryApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

