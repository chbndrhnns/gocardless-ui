import argparse
import asyncio

from server.src.services.sync_service import get_token_storage, sync_transactions


async def main(account_id, days_to_sync):
    token_storage = get_token_storage()
    await sync_transactions(token_storage, account_id, days_to_sync=days_to_sync)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync transactions for an account.")
    parser.add_argument(
        "account_id", type=str, help="The ID of the account to sync transactions for."
    )
    parser.add_argument(
        "--days-to-sync",
        type=int,
        help="Number of days to sync transactions.",
        default=None,
    )
    args = parser.parse_args()

    asyncio.run(main(args.account_id, args.days_to_sync))
