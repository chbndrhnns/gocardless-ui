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
    requisitions = await get_requisitions()
    return requisitions


@router.get("/{id}")
async def get_details(id: str):
    details = await get_requisition_details(id)
    return details


@router.post("/")
async def create(request: CreateRequisitionRequest):
    requisition = await create_new_requisition(request.dict())
    return requisition


@router.delete("/{id}")
async def delete(id: str):
    await remove_requisition(id)
    return {"status": "success"}
