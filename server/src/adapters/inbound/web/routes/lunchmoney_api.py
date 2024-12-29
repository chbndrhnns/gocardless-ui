"""Lunch Money API routes."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from server.src.core.domain.models import AccountLink
from server.src.core.ports.repositories import AccountLinkRepository
from server.src.core.ports.services import LunchMoneyService
from server.src.adapters.inbound.web.dependencies import (
    get_account_link_repository,
    get_lunchmoney_service,
)

router = APIRouter()


class LinkAccountsRequest(BaseModel):
    lunchmoneyId: int
    gocardlessId: str


class UnlinkAccountsRequest(BaseModel):
    lunchmoneyId: int
    gocardlessId: str


@router.get("/assets")
async def list_assets(
    lunchmoney_service: LunchMoneyService = Depends(get_lunchmoney_service),
    account_link_repository: AccountLinkRepository = Depends(
        get_account_link_repository
    ),
):
    assets = await lunchmoney_service.get_assets()
    links = await account_link_repository.load_links()

    # Add linked status to each asset
    assets_with_links = [
        {
            **asset,
            "linked_account": next(
                (
                    link.gocardless_id
                    for link in links
                    if link.lunchmoney_id == asset["id"]
                ),
                None,
            ),
        }
        for asset in assets
    ]

    return {"assets": assets_with_links}


@router.post("/link")
async def link(
    request: LinkAccountsRequest,
    account_link_repository: AccountLinkRepository = Depends(
        get_account_link_repository
    ),
):
    link = AccountLink(
        lunchmoney_id=request.lunchmoneyId,
        gocardless_id=request.gocardlessId,
        created_at=datetime.now().isoformat(),
    )
    account_link_repository.save_link(link)
    return {"message": "Accounts linked successfully"}


@router.post("/unlink")
async def unlink(
    request: UnlinkAccountsRequest,
    account_link_repository: AccountLinkRepository = Depends(
        get_account_link_repository
    ),
):
    account_link_repository.remove_link(request.lunchmoneyId, request.gocardlessId)
    return {"message": "Account unlinked successfully"}
