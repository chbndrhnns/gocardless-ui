from typing import List
from .models import Requisition
from .ports import RequisitionPort, AccountPort


class RequisitionService:
    """Domain service for requisition operations."""

    def __init__(self, requisition_port: RequisitionPort, account_port: AccountPort):
        self.requisition_port = requisition_port
        self.account_port = account_port

    async def get_requisitions(self) -> List[Requisition]:
        """Get all requisitions sorted by creation date."""
        requisitions = await self.requisition_port.get_requisitions()
        return sorted(requisitions, key=lambda x: x.created)

    async def get_requisition_details(self, requisition_id: str) -> Requisition:
        """Get detailed requisition information."""
        return await self.requisition_port.get_requisition_details(requisition_id)

    async def delete_requisition(self, requisition_id: str) -> None:
        """Delete a requisition."""
        await self.requisition_port.delete_requisition(requisition_id)
