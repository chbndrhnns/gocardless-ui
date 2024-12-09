from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.lunchmoney import link_accounts, unlink_accounts, get_assets

router = APIRouter()


class LinkAccountsRequest(BaseModel):
    lunchmoneyId: int
    gocardlessId: str


@router.get("/assets")
async def list_assets():
    assets = await get_assets()
    return {"assets": assets}


@router.post("/link")
async def link(request: LinkAccountsRequest):
    link_accounts(request.lunchmoneyId, request.gocardlessId)
    return {"message": "Accounts linked successfully"}


@router.post("/unlink")
async def unlink(request: LinkAccountsRequest):
    unlink_accounts(request.lunchmoneyId)
    return {"message": "Account unlinked successfully"}
