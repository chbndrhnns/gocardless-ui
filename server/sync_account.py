import argparse
import asyncio
import json
from pathlib import Path

from server.src.services.sync_service import get_token_storage, sync_transactions


async def main(account_id, days_to_sync, data_file):
    token_storage = get_token_storage()
    data = None
    if data_file:
        data = json.loads(Path(data_file).read_text())
    await sync_transactions(
        token_storage, account_id, days_to_sync=days_to_sync, tx_data=data
    )


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
    parser.add_argument(
        "--data-file",
        type=str,
        help="Path to the JSON file containing transaction data.",
        default=None,
    )

    args = parser.parse_args()

    asyncio.run(main(args.account_id, args.days_to_sync, args.data_file))
