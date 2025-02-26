from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Account:
    id: str
    iban: Optional[str]
    currency: Optional[str]
    status: str


@dataclass
class Requisition:
    id: str
    institution_id: str
    status: str
    created: datetime
    accounts: List[Account]

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until requisition expires (90 days from creation)."""
        from datetime import timezone, timedelta

        expiry_date = self.created + timedelta(days=90)
        today = datetime.now(tz=timezone.utc)
        delta = expiry_date - today
        return delta.days

    @property
    def expiry_status(self) -> str:
        """Return the expiry status for UI display."""
        days = self.days_until_expiry
        if days < 0:
            return "expired"
        elif days < 14:
            return "expiring_soon"
        return "active"
