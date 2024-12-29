"""Institution API routes."""

from fastapi import APIRouter, Depends, Query

from server.src.core.ports.services import InstitutionService
from server.src.adapters.inbound.web.dependencies import get_institution_service

router = APIRouter()


@router.get("/")
async def list_institutions(
    country: str = Query(..., description="Country code"),
    institution_service: InstitutionService = Depends(get_institution_service),
):
    """Get list of institutions for a country."""
    institutions = await institution_service.get_institutions(country)
    return institutions
