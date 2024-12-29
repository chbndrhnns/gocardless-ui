"""Service interfaces for external integrations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from server.src.core.domain.models import (
    TokenInfo,
    Transaction,
    Institution,
    Requisition,
)


class TokenService(ABC):
    @abstractmethod
    def get_token(self) -> str:
        """Get a valid access token."""
        pass

    @abstractmethod
    def refresh_token(self) -> str:
        """Refresh the access token."""
        pass

    @abstractmethod
    def create_token(self) -> TokenInfo:
        """Create a new token pair."""
        pass


class GoCardlessService(ABC):
    @abstractmethod
    async def get_account_details(
        self, account_id: str, access_token: str
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Get account details from GoCardless."""
        pass

    @abstractmethod
    async def get_transactions(
        self,
        account_id: str,
        access_token: str,
        from_date: str,
        to_date: Optional[str] = None,
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Get transactions from GoCardless."""
        pass


class LunchMoneyService(ABC):
    @abstractmethod
    async def get_assets(self) -> List[Dict[str, Any]]:
        """Get assets from Lunch Money."""
        pass

    @abstractmethod
    async def get_transactions(
        self, asset_id: int, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """Get transactions from Lunch Money."""
        pass

    @abstractmethod
    async def create_transactions(
        self, transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Create transactions in Lunch Money."""
        pass


class InstitutionService(ABC):
    @abstractmethod
    async def get_institutions(self, country: str) -> list[Institution]:
        """Get list of institutions for a country."""
        pass


class RequisitionService(ABC):
    @abstractmethod
    async def get_requisitions(self) -> list[Requisition]:
        """Get all requisitions."""
        pass

    @abstractmethod
    async def get_requisition_details(self, requisition_id: str) -> Dict[str, Any]:
        """Get details for a specific requisition."""
        pass

    @abstractmethod
    async def create_requisition(self, params: Dict[str, Any]) -> Requisition:
        """Create a new requisition."""
        pass

    @abstractmethod
    async def delete_requisition(self, requisition_id: str) -> None:
        """Delete a requisition."""
        pass
