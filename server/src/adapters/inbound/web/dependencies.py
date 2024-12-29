"""FastAPI dependency injection configuration."""

import os
from functools import lru_cache

from ....core.services.sync_service import SyncService
from server.src.core.ports.repositories import (
    AccountLinkRepository,
    SyncStatusRepository,
)
from server.src.core.ports.services import (
    GoCardlessService,
    InstitutionService,
    LunchMoneyService,
    RequisitionService,
    TokenService,
)
from ...outbound.file_storage import FileAccountLinkRepository, FileSyncStatusRepository
from server.src.adapters.outbound.gocardless import (
    GoCardlessApiAdapter,
    GoCardlessInstitutionAdapter,
    GoCardlessRequisitionAdapter,
    GoCardlessTokenAdapter,
)
from ...outbound.lunchmoney import LunchMoneyApiAdapter


@lru_cache
def get_token_service() -> TokenService:
    return GoCardlessTokenAdapter()


@lru_cache
def get_gocardless_service() -> GoCardlessService:
    return GoCardlessApiAdapter()


@lru_cache
def get_institution_service() -> InstitutionService:
    return GoCardlessInstitutionAdapter()


@lru_cache
def get_requisition_service() -> RequisitionService:
    return GoCardlessRequisitionAdapter()


@lru_cache
def get_lunchmoney_service() -> LunchMoneyService:
    return LunchMoneyApiAdapter()


@lru_cache
def get_account_link_repository() -> AccountLinkRepository:
    return FileAccountLinkRepository()


@lru_cache
def get_sync_status_repository() -> SyncStatusRepository:
    return FileSyncStatusRepository()


@lru_cache
def get_sync_service() -> SyncService:
    return SyncService(
        token_service=get_token_service(),
        gocardless_service=get_gocardless_service(),
        lunchmoney_service=get_lunchmoney_service(),
        account_link_repository=get_account_link_repository(),
        sync_status_repository=get_sync_status_repository(),
        days_to_sync=int(os.getenv("DAYS_TO_SYNC", "30")),
    )
