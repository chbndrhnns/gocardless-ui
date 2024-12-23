from fastapi import APIRouter

from ..services.accounts import get_account_details

router = APIRouter()


@router.get("/{id}")
async def get_account(id: str):
    account = await get_account_details(id)
    return account
