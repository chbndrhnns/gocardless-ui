"""Domain models representing core business entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    date: str
    amount: str
    currency: str
    payee: str
    notes: str
    asset_id: int
    external_id: str
    status: str = "uncleared"


@dataclass
class RateLimit:
    limit: int
    remaining: int
    reset: Optional[str]


@dataclass
class AccountStatus:
    last_sync: Optional[str] = None
    last_sync_status: Optional[str] = None
    last_sync_transactions: int = 0
    is_syncing: bool = False
    rate_limit: Optional[RateLimit] = None


@dataclass
class AccountLink:
    lunchmoney_id: int
    gocardless_id: str
    created_at: str


@dataclass
class TokenInfo:
    access_token: str
    refresh_token: str
    access_expires: datetime
    refresh_expires: datetime


@dataclass
class Institution:
    id: str
    name: str
    bic: str
    transaction_total_days: int
    countries: list[str]
    logo: str


@dataclass
class Requisition:
    id: str
    created: str
    status: str  # CR, LN, RJ, ER, EX, GA
    institution_id: str
    agreement: str
    reference: str
    accounts: list[str]
    user_language: str
    link: str
    ssn: Optional[str] = None
    account_selection: bool = False
    redirect: Optional[str] = None
    redirect_immediate: bool = False
