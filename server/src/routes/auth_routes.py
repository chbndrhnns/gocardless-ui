from fastapi import APIRouter

from ..services.auth import get_access_token

router = APIRouter()


@router.post("/token")
async def token():
    token = get_access_token()
    return token
