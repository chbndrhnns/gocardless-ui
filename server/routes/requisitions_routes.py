from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.requisitions import (
    get_requisition_details,
    create_new_requisition,
    remove_requisition,
    get_requisitions,
)

router = APIRouter()


class CreateRequisitionRequest(BaseModel):
    institution_id: str
    redirect: str
    reference: str
    user_language: str


@router.get("/")
async def list_requisitions():
    try:
        requisitions = await get_requisitions()
        return requisitions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}")
async def get_details(id: str):
    try:
        details = await get_requisition_details(id)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create(request: CreateRequisitionRequest):
    try:
        requisition = await create_new_requisition(request.dict())
        return requisition
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}")
async def delete(id: str):
    try:
        await remove_requisition(id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
