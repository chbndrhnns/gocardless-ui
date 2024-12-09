from fastapi import APIRouter, HTTPException
from server.services.auth import get_access_token

router = APIRouter()


@router.post("/token")
async def token():
    try:
        token = get_access_token()
        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
