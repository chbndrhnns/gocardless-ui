"""Sync service implementation."""

import logging
from datetime import datetime, timedelta

from ..domain import AccountLink, AccountStatus, RateLimit, Transaction
from ..ports import AccountLinkRepository, SyncStatusRepository
from ..ports import GoCardlessService, LunchMoneyService, TokenService

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(
        self,
        token_service: TokenService,
        gocardless_service: GoCardlessService,
        lunchmoney_service: LunchMoneyService,
        account_link_repository: AccountLinkRepository,
        sync_status_repository: SyncStatusRepository,
        days_to_sync: int = 30,
    ):
        self.token_service = token_service
        self.gocardless_service = gocardless_service
        self.lunchmoney_service = lunchmoney_service
        self.account_link_repository = account_link_repository
        self.sync_status_repository = sync_status_repository
        self.days_to_sync = days_to_sync

    async def sync_transactions(self, account_id: str | None = None) -> None:
        """Sync transactions for one or all accounts."""
        account_links = await self.account_link_repository.load_links(account_id)
        access_token = self.token_service.get_token()
        now = datetime.now()

        for link in account_links:
            await self._sync_account_transactions(link, access_token, now)

    async def _sync_account_transactions(
        self, link: AccountLink, access_token: str, now: datetime
    ) -> None:
        """Sync transactions for a single account."""
        logger.info(f"Syncing transactions for account {link.gocardless_id}")

        # Update sync status to indicate sync in progress
        status = AccountStatus(is_syncing=True, last_sync_status="pending")
        await self.sync_status_repository.save_status(link.gocardless_id, status)

        try:
            # Calculate date range
            from_date = (now - timedelta(days=self.days_to_sync)).date().isoformat()

            # Fetch transactions from GoCardless
            (
                transactions_data,
                rate_limits,
            ) = await self.gocardless_service.get_transactions(
                link.gocardless_id, access_token, from_date
            )

            # Transform and sync transactions
            all_transactions = []
            for tx_type in ["booked"]:  # Currently only processing booked transactions
                transformed_transactions = [
                    await self._transform_transaction(tx, link.lunchmoney_id)
                    for tx in transactions_data.get(tx_type, [])
                ]
                all_transactions.extend(transformed_transactions)

            # Send to Lunch Money
            result = await self._sync_to_lunchmoney(all_transactions)

            # Update sync status with success
            status = AccountStatus(
                last_sync=now.isoformat(),
                last_sync_status="success",
                last_sync_transactions=len(result),
                is_syncing=False,
                rate_limit=RateLimit(**rate_limits) if rate_limits else None,
            )

        except Exception as e:
            logger.error(f"Sync failed for account {link.gocardless_id}: {str(e)}")
            status = AccountStatus(
                last_sync=now.isoformat(), last_sync_status="error", is_syncing=False
            )

        await self.sync_status_repository.save_status(link.gocardless_id, status)

    async def _sync_to_lunchmoney(self, transactions: list[Transaction]) -> list[dict]:
        """Sync transactions to Lunch Money, handling duplicates."""
        if not transactions:
            return []

        # Get date range from transactions
        dates = [tx.date for tx in transactions]
        start_date = min(dates)
        end_date = max(dates)

        # Fetch existing transactions
        existing_transactions = await self.lunchmoney_service.get_transactions(
            transactions[0].asset_id, start_date, end_date
        )
        existing_ids = {tx["external_id"] for tx in existing_transactions}

        # Filter out existing transactions
        new_transactions = [
            tx for tx in transactions if tx.external_id not in existing_ids
        ]

        if not new_transactions:
            logger.info("No new transactions to sync")
            return []

        return await self.lunchmoney_service.create_transactions(new_transactions)

    async def _transform_transaction(
        self, tx_data: dict, lunchmoney_id: int
    ) -> Transaction:
        """Transform GoCardless transaction to domain model."""
        raw_notes = tx_data.get("remittanceInformationUnstructured", "")
        notes = (
            raw_notes
            if "remittanceinformation:" not in raw_notes
            else raw_notes.split("remittanceinformation:")[1].strip()
        )

        payee = (
            tx_data.get("merchantName")
            or tx_data.get("creditorName")
            or tx_data.get("debtorName", "Unknown")
        )

        return Transaction(
            date=datetime.fromisoformat(tx_data["bookingDate"]).date().isoformat(),
            amount=f"{float(tx_data['transactionAmount']['amount']):.2f}",
            currency=(tx_data["transactionAmount"]["currency"]).lower(),
            payee=payee.strip(),
            notes=notes.strip(),
            asset_id=lunchmoney_id,
            external_id=tx_data["internalTransactionId"],
        )
