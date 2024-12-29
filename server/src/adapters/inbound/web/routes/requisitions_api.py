"""Requisition API routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from server.src.core.ports.services import RequisitionService
from server.src.adapters.inbound.web.dependencies import get_requisition_service

router = APIRouter()


class CreateRequisitionRequest(BaseModel):
    institution_id: str
    redirect: str
    reference: str
    user_language: str


@router.get("/")
async def list_requisitions(
    requisition_service: RequisitionService = Depends(get_requisition_service),
):
    """Get all requisitions."""
    requisitions = await requisition_service.get_requisitions()
    return {"results": requisitions}


@router.get("/{id}")
async def get_details(
    id: str,
    requisition_service: RequisitionService = Depends(get_requisition_service),
):
    """Get details for a specific requisition."""
    details = await requisition_service.get_requisition_details(id)
    return details


@router.post("/")
async def create(
    request: CreateRequisitionRequest,
    requisition_service: RequisitionService = Depends(get_requisition_service),
):
    """Create a new requisition."""
    requisition = await requisition_service.create_requisition(request.model_dump())
    return requisition


@router.delete("/{id}")
async def delete(
    id: str,
    requisition_service: RequisitionService = Depends(get_requisition_service),
):
    """Delete a requisition."""
    await requisition_service.delete_requisition(id)
    return {"status": "success"}
