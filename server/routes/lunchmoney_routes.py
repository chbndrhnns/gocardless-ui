from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.lunchmoney import link_accounts, unlink_accounts, get_assets

router = APIRouter()


class LinkAccountsRequest(BaseModel):
    lunchmoneyId: int
    gocardlessId: str


@router.get("/assets")
async def list_assets():
    try:
        assets = await get_assets()
        return {"assets": assets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/link")
async def link(request: LinkAccountsRequest):
    try:
        link_accounts(request.lunchmoneyId, request.gocardlessId)
        return {"message": "Accounts linked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unlink")
async def unlink(request: LinkAccountsRequest):
    try:
        unlink_accounts(request.lunchmoneyId)
        return {"message": "Account unlinked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
