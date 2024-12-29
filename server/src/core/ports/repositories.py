"""Repository interfaces for data persistence."""

from abc import ABC, abstractmethod
from typing import List, Optional

from server.src.core.domain.models import AccountLink, AccountStatus


class AccountLinkRepository(ABC):
    @abstractmethod
    async def load_links(self, account_id: Optional[str] = None) -> List[AccountLink]:
        """Load account links, optionally filtered by account ID."""
        pass

    @abstractmethod
    def save_link(self, link: AccountLink) -> None:
        """Save a new account link."""
        pass

    @abstractmethod
    def remove_link(self, lunchmoney_id: int, gocardless_id: str) -> None:
        """Remove an account link."""
        pass


class SyncStatusRepository(ABC):
    @abstractmethod
    async def get_status(self, account_id: str) -> AccountStatus:
        """Get sync status for an account."""
        pass

    @abstractmethod
    async def save_status(self, account_id: str, status: AccountStatus) -> None:
        """Save sync status for an account."""
        pass

    @abstractmethod
    async def reset_sync_status(self) -> None:
        """Reset sync status for all accounts."""
        pass
