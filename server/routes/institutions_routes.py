from fastapi import APIRouter, HTTPException, Query
from server.services.institutions import get_institutions

router = APIRouter()


@router.get("/")
async def list_institutions(country: str = Query(..., description="Country code")):
    try:
        institutions = await get_institutions(country)
        return institutions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
