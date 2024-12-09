from fastapi import APIRouter, HTTPException, Query
from server.services.institutions import get_institutions

router = APIRouter()


@router.get("/")
async def list_institutions(country: str = Query(..., description="Country code")):
    institutions = await get_institutions(country)
    return institutions
