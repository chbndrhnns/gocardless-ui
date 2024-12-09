from fastapi import APIRouter, HTTPException
from server.services.accounts import get_account_details

router = APIRouter()


@router.get("/{id}")
async def get_account(id: str):
    try:
        account = await get_account_details(id)
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
