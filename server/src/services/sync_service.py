import json
import logging
import os
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path

import httpx
from dotenv import load_dotenv

project_dir = Path(__file__).parents[2]
load_dotenv()


# Set up logging
logging.basicConfig(
    level=os.getenv("BACKEND_LOG_LEVEL"),
    format="%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)

# Configuration
GOCARDLESS_API_URL = "https://bankaccountdata.gocardless.com/api/v2"
GOCARDLESS_SECRET_ID = os.environ.get("GOCARDLESS_SECRET_ID")
if not GOCARDLESS_SECRET_ID:
    raise ValueError("GOCARDLESS_SECRET_ID is not set in the environment")
GOCARDLESS_SECRET_KEY = os.environ.get("GOCARDLESS_SECRET_KEY")
if not GOCARDLESS_SECRET_KEY:
    raise ValueError("GOCARDLESS_SECRET_KEY is not set in the environment")
LUNCHMONEY_API_URL = "https://dev.lunchmoney.app/v1"
LUNCHMONEY_API_KEY = os.environ.get("LUNCHMONEY_ACCESS_TOKEN")
if not LUNCHMONEY_API_KEY:
    raise ValueError("LUNCHMONEY_ACCESS_TOKEN is not set in the environment")
ACCOUNT_LINKS_FILE = Path(project_dir / "data" / "account-links.json")
logger.debug("Reading account links from file: %s", ACCOUNT_LINKS_FILE)
SYNC_STATUS_FILE = Path(project_dir / "data" / "sync-status.json")
logger.debug("Reading account links from file: %s", ACCOUNT_LINKS_FILE)
HTTP_REQUEST_TIMEOUT = 30
DAYS_TO_SYNC = int(os.environ.get("DAYS_TO_SYNC", "14"))


class TokenStorage:
    def __init__(self):
        self.gocardless_token = None
        self.token_expiry = None


@lru_cache
def get_token_storage() -> TokenStorage:
    return TokenStorage()


async def extract_rate_limits(headers: httpx.Headers) -> dict:
    seconds_until_reset = int(headers.get("HTTP_X_RATELIMIT_ACCOUNT_SUCCESS_RESET", 0))
    delta = (
        timedelta(seconds=seconds_until_reset)
        if seconds_until_reset
        else timedelta(hours=24)
    )
    reset_timestamp = (datetime.now(timezone.utc) + delta).isoformat()
    rate_limits = {
        "limit": int(headers.get("HTTP_X_RATELIMIT_ACCOUNT_SUCCESS_LIMIT", 0)),
        "remaining": int(headers.get("HTTP_X_RATELIMIT_ACCOUNT_SUCCESS_REMAINING", 0)),
        "reset": reset_timestamp,
    }
    return rate_limits


async def load_account_links(account_id=None) -> list[dict]:
    if not ACCOUNT_LINKS_FILE.exists():
        return []
    with open(ACCOUNT_LINKS_FILE) as f:
        content = f.read()
        links = json.loads(content)["links"]

        if account_id:
            links = [link for link in links if link["gocardlessId"] == account_id]

        return links


async def load_sync_status() -> dict:
    if not SYNC_STATUS_FILE.exists():
        return {}
    with open(SYNC_STATUS_FILE) as f:
        return json.load(f)


async def save_sync_status(status: dict):
    SYNC_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SYNC_STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


async def reset_sync_status():
    sync_status = await load_sync_status()
    for account_id in sync_status:
        if sync_status[account_id].get("isSyncing"):
            logger.info(
                f"Resetting sync status for account {account_id}: isSyncing -> false"
            )
            sync_status[account_id]["isSyncing"] = False
        if sync_status[account_id].get("lastSyncStatus") == "pending":
            logger.info(
                f"Resetting sync status for account {account_id}: lastSyncStatus -> error"
            )
            sync_status[account_id]["lastSyncStatus"] = "error"
    await save_sync_status(sync_status)


async def get_next_sync_time() -> str:
    now = datetime.now(timezone.utc)
    next_sync = now.replace(
        hour=((now.hour // 3) * 3 + 3) % 24, minute=0, second=0, microsecond=0
    )
    if next_sync <= now:
        next_sync += timedelta(hours=3)
    return next_sync.isoformat()


async def get_gocardless_token(token_storage: TokenStorage) -> str:
    if (
        token_storage.gocardless_token
        and token_storage.token_expiry
        and datetime.now(timezone.utc) < token_storage.token_expiry
    ):
        return token_storage.gocardless_token

    url = f"{GOCARDLESS_API_URL}/token/new/"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"secret_id": GOCARDLESS_SECRET_ID, "secret_key": GOCARDLESS_SECRET_KEY}

    response = httpx.post(url, headers=headers, json=data, timeout=HTTP_REQUEST_TIMEOUT)
    response.raise_for_status()
    token_data = response.json()

    token_storage.gocardless_token = token_data["access"]
    token_storage.token_expiry = datetime.now(timezone.utc) + timedelta(
        seconds=token_data["access_expires"]
    )

    return token_storage.gocardless_token


async def get_gocardless_account_details(
    account_id: str, access_token: str
) -> tuple[dict, dict]:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = httpx.get(
        url, headers=headers, follow_redirects=True, timeout=HTTP_REQUEST_TIMEOUT
    )
    response.raise_for_status()
    rate_limits = await extract_rate_limits(response.headers)
    return response.json(), rate_limits


async def get_gocardless_account_name(account_id: str, access_token: str) -> str:
    account_data, _ = await get_gocardless_account_details(account_id, access_token)
    return account_data.get("iban", "Unknown Account")


async def get_lunchmoney_account_name(account_id: int, accounts_dict: dict) -> str:
    return accounts_dict.get(account_id, "Unknown Account")


async def get_account_status(account_id: str) -> dict:
    sync_status = await load_sync_status()
    account_status = sync_status.get(account_id, {})

    if not account_status:
        account_status = {
            "lastSync": None,
            "lastSyncStatus": None,
            "lastSyncTransactions": 0,
            "isSyncing": False,
            "rateLimit": {"limit": -1, "remaining": -1, "reset": None},
        }

    account_status["nextSync"] = await get_next_sync_time()
    return account_status


async def fetch_all_lunchmoney_accounts():
    url = f"{LUNCHMONEY_API_URL}/assets/"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json",
    }

    response = httpx.get(
        url, headers=headers, follow_redirects=True, timeout=HTTP_REQUEST_TIMEOUT
    )
    response.raise_for_status()
    accounts = response.json().get("assets", [])
    return {account["id"]: account["name"] for account in accounts}


async def sync_transactions(token_storage: TokenStorage, account_id=None):
    if account_id:
        logger.info(f"Syncing transactions for account {account_id}")
    else:
        logger.info(f"Syncing transactions all accounts")

    account_links = await load_account_links(account_id)
    sync_status = await load_sync_status()
    now = datetime.now(timezone.utc)
    access_token = await get_gocardless_token(token_storage)

    for link in account_links:
        account_id = link["gocardlessId"]
        logging.info(f"Fetching transactions for account {account_id}")
        from_date = (
            (
                datetime.fromisoformat(link.get("lastSync", now.isoformat()))
                - timedelta(days=DAYS_TO_SYNC)
            )
            .date()
            .isoformat()
        )
        # Update sync status
        if account_id not in sync_status:
            sync_status[account_id] = {}
        sync_status[account_id]["isSyncing"] = True
        sync_status[account_id]["lastSyncStatus"] = "pending"
        await save_sync_status(sync_status)

        try:
            gocardless_data, rate_limits = await get_gocardless_transactions(
                link["gocardlessId"], access_token, from_date
            )

            # Check and adjust rate limits
            if rate_limits:
                reset_time = datetime.fromisoformat(rate_limits["reset"])
                if now >= reset_time:
                    rate_limits["limit"] = -1
                    rate_limits["remaining"] = -1
                    rate_limits["reset"] = None

            all_transactions = []
            for tx_type in [
                "booked",
                # "pending",
            ]:
                transformed_transactions = [
                    await transform_transaction(tx, link["lunchmoneyId"])
                    for tx in gocardless_data.get(tx_type, [])
                ]
                all_transactions.extend(transformed_transactions)
            try:
                result = await send_transactions_to_lunchmoney(all_transactions)
                logging.info(
                    f"Synced {len(all_transactions)} transactions for account {link['gocardlessId']}. Lunch Money response: {result}"
                )
            except Exception as e:
                logging.error(
                    f"Error sending transactions to Lunch Money for account {link['gocardlessId']}: {str(e)}"
                )
            # Update sync status with the calculated rate limits
            sync_status[account_id].update(
                {
                    "lastSync": datetime.now(timezone.utc).isoformat(),
                    "lastSyncStatus": "success",
                    "lastSyncTransactions": len(result),
                    "isSyncing": False,
                    "rateLimit": rate_limits,
                }
            )
        except Exception as e:
            logger.error(f"Sync failed for account {account_id}: {str(e)}")
            sync_status[account_id].update(
                {
                    "lastSync": now.isoformat(),
                    "lastSyncStatus": "error",
                    "isSyncing": False,
                }
            )
        await save_sync_status(sync_status)


async def get_gocardless_transactions(
    account_id: str, access_token: str, from_date: str, to_date: str = None
) -> tuple[dict, dict]:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}/transactions/"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"date_from": from_date} | ({"date_to": to_date} if to_date else {})

    response = httpx.get(url, headers=headers, params=params, follow_redirects=True)
    rate_limits = await extract_rate_limits(response.headers)
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        logger.warning(f"Rate limit exceeded for account {account_id}: {rate_limits}")
        return {}, rate_limits
    if (
        HTTPStatus.BAD_REQUEST
        <= response.status_code
        < HTTPStatus.INTERNAL_SERVER_ERROR
    ):
        logger.error(
            f"Error fetching transactions for account {account_id}: {response.text}"
        )
    response.raise_for_status()

    result = response.json()["transactions"]
    logger.debug(f"Received transactions for account {account_id}: {result}")

    return result, rate_limits


async def send_transactions_to_lunchmoney(transactions):
    """Send new transactions to Lunch Money."""
    # Determine start_date and end_date from transaction batch
    dates = [tx["date"] for tx in transactions]
    start_date = min(dates or datetime.now())
    end_date = max(dates or datetime.now())

    # Fetch existing transactions
    existing_transactions = await fetch_existing_transactions(
        transactions[0]["asset_id"], start_date, end_date
    )
    existing_ids = {tx["external_id"] for tx in existing_transactions}

    # Filter out transactions where external_id matches
    new_transactions = [
        tx for tx in transactions if tx["external_id"] not in existing_ids
    ]

    if not new_transactions:
        logger.info("No new transactions to send to Lunch Money.")
        return []

    return await send_batch(new_transactions)


async def fetch_existing_transactions(asset_id, start_date, end_date):
    """Fetch existing transactions from Lunch Money."""
    url = f"{LUNCHMONEY_API_URL}/transactions"
    headers = {"Authorization": f"Bearer {LUNCHMONEY_API_KEY}"}
    params = {"asset_id": asset_id, "start_date": start_date, "end_date": end_date}

    response = httpx.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("transactions", [])


async def send_batch(transactions: list[dict]) -> list[dict]:
    url = f"{LUNCHMONEY_API_URL}/transactions/"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json",
    }
    all_responses = []
    for start in range(0, len(transactions), 500):
        batch = transactions[start : start + 500]
        data = {
            "transactions": batch,
            "check_for_recurring": True,
            "debit_as_negative": True,
        }
        logger.info(f"Sending {len(batch)} transactions to Lunch Money.")
        response = httpx.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.debug(response.json())
        all_responses.append(response.json())
    return all_responses


async def transform_transaction(
    gocardless_tx: dict, lunchmoney_account_id: int
) -> dict:
    logger.debug(f"Transforming transaction: {gocardless_tx}")
    raw_notes = gocardless_tx.get("remittanceInformationUnstructured", "")
    notes = (
        raw_notes
        if "remittanceinformation:" not in raw_notes
        else raw_notes.split("remittanceinformation:")[1].strip()
    )
    payee = (
        gocardless_tx.get("merchantName", None)
        or gocardless_tx.get("creditorName", None)
        or gocardless_tx.get("debtorName", "Unknown")
    )
    parsed = {
        "date": datetime.fromisoformat(gocardless_tx["bookingDate"]).date().isoformat(),
        "amount": f"{float(gocardless_tx['transactionAmount']['amount']):.2f}",
        "currency": (gocardless_tx["transactionAmount"]["currency"]).lower(),
        "payee": payee.strip(),
        "notes": notes.strip(),
        "asset_id": lunchmoney_account_id,
        "external_id": gocardless_tx["internalTransactionId"],
        "status": "uncleared",
    }
    logger.debug(f"Transformed transaction: {parsed}")
    return parsed
