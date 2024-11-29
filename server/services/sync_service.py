import json
import logging
import os
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path

import httpx
from flask.cli import load_dotenv

DAYS_TO_SYNC = 14

project_dir = Path(__file__).parents[2]
load_dotenv(os.path.join(project_dir, ".env"))

# Set up logging
logging.basicConfig(
    level=os.getenv("BACKEND_LOG_LEVEL"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)

# Configuration
GOCARDLESS_API_URL = "https://bankaccountdata.gocardless.com/api/v2"
GOCARDLESS_SECRET_ID = os.environ.get("VITE_SECRET_ID")
GOCARDLESS_SECRET_KEY = os.environ.get("VITE_SECRET_KEY")
LUNCHMONEY_API_URL = "https://dev.lunchmoney.app/v1"
LUNCHMONEY_API_KEY = os.environ.get("LUNCHMONEY_ACCESS_TOKEN")
ACCOUNT_LINKS_FILE = Path(project_dir / "server" / "data" / "account-links.json")
SYNC_STATUS_FILE = Path(project_dir / "server" / "data" / "sync-status.json")
HTTP_REQUEST_TIMEOUT = 30


class TokenStorage:
    def __init__(self):
        self.gocardless_token = None
        self.token_expiry = None


@lru_cache
def get_token_storage() -> TokenStorage:
    return TokenStorage()


def extract_rate_limits(headers: httpx.Headers) -> dict:
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


def load_account_links(account_id=None) -> list[dict]:
    if not ACCOUNT_LINKS_FILE.exists():
        return []
    with open(ACCOUNT_LINKS_FILE) as f:
        content = f.read()
        links = json.loads(content)["links"]

        if account_id:
            links = [link for link in links if link["gocardlessId"] == account_id]

        return links


def load_sync_status() -> dict:
    if not SYNC_STATUS_FILE.exists():
        return {}
    with open(SYNC_STATUS_FILE) as f:
        return json.load(f)


def save_sync_status(status: dict):
    SYNC_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SYNC_STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def get_next_sync_time() -> str:
    now = datetime.now(timezone.utc)
    next_sync = now.replace(
        hour=((now.hour // 3) * 3 + 3) % 24, minute=0, second=0, microsecond=0
    )
    if next_sync <= now:
        next_sync += timedelta(hours=3)
    return next_sync.isoformat()


def get_gocardless_token(token_storage: TokenStorage) -> str:
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


def get_gocardless_account_details(
    account_id: str, access_token: str
) -> tuple[dict, dict]:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = httpx.get(
        url, headers=headers, follow_redirects=True, timeout=HTTP_REQUEST_TIMEOUT
    )
    response.raise_for_status()
    rate_limits = extract_rate_limits(response.headers)
    return response.json(), rate_limits


def get_gocardless_account_name(account_id: str, access_token: str) -> str:
    account_data, _ = get_gocardless_account_details(account_id, access_token)
    return account_data.get("iban", "Unknown Account")


def get_lunchmoney_account_name(account_id: int) -> str:
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
    for account in accounts:
        if account["id"] == account_id:
            return account.get("name", "Unknown Account")
    return "Unknown Account"


def get_account_status(account_id: str, access_token: str) -> dict:
    sync_status = load_sync_status()
    account_status = sync_status.get(account_id, {})

    if not account_status:
        account_status = {
            "lastSync": None,
            "lastSyncStatus": None,
            "lastSyncTransactions": 0,
            "isSyncing": False,
        }

    # Get fresh rate limits
    _, rate_limits = get_gocardless_account_details(account_id, access_token)
    account_status["rateLimit"] = rate_limits
    account_status["nextSync"] = get_next_sync_time()

    return account_status


def sync_transactions(token_storage: TokenStorage, account_id=None):
    account_links = load_account_links(account_id)
    sync_status = load_sync_status()
    now = datetime.now(timezone.utc)

    access_token = get_gocardless_token(token_storage)

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
        save_sync_status(sync_status)

        try:
            gocardless_data, rate_limits = get_gocardless_transactions(
                link["gocardlessId"], access_token, from_date
            )

            all_transactions = []
            for tx_type in [
                "booked",
                # "pending",
            ]:
                transformed_transactions = [
                    transform_transaction(tx, link["lunchmoneyId"])
                    for tx in gocardless_data.get(tx_type, [])
                ]
                all_transactions.extend(transformed_transactions)

            try:
                result = send_transactions_to_lunchmoney(all_transactions)
                logging.info(
                    f"Synced {len(all_transactions)} transactions for account {link['gocardlessId']}. Lunch Money response: {result}"
                )
            except Exception as e:
                logging.error(
                    f"Error sending transactions to Lunch Money for account {link['gocardlessId']}: {str(e)}"
                )

            # For now, we'll just simulate a successful sync
            sync_status[account_id].update(
                {
                    "lastSync": datetime.now(timezone.utc).isoformat(),
                    "lastSyncStatus": "success",
                    "lastSyncTransactions": len(all_transactions),
                    "isSyncing": False,
                    "rateLimit": rate_limits,
                }
            )
            logging.info(
                f"Fetched {len(all_transactions)} transactions for account {link['gocardlessId']}"
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

        save_sync_status(sync_status)


def get_gocardless_transactions(
    account_id: str, access_token: str, from_date: str, to_date: str = None
) -> tuple[dict, dict]:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}/transactions/"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"date_from": from_date} | ({"date_to": to_date} if to_date else {})

    response = httpx.get(url, headers=headers, params=params, follow_redirects=True)
    rate_limits = extract_rate_limits(response.headers)
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        logger.warning(f"Rate limit exceeded for account {account_id}: {rate_limits}")
        return {}, rate_limits
    response.raise_for_status()

    result = response.json()["transactions"]
    logger.debug(f"Received transactions for account {account_id}: {result}")

    # Extract and return rate limits with transactions
    rate_limits = extract_rate_limits(response.headers)
    return result, rate_limits


def send_transactions_to_lunchmoney(transactions):
    """Send new transactions to Lunch Money."""
    # Determine start_date and end_date from transaction batch
    dates = [tx["date"] for tx in transactions]
    start_date = min(dates or datetime.now())
    end_date = max(dates or datetime.now())

    # Fetch existing transactions
    existing_transactions = fetch_existing_transactions(
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

    return send_batch(new_transactions)


def fetch_existing_transactions(asset_id, start_date, end_date):
    """Fetch existing transactions from Lunch Money."""
    url = f"{LUNCHMONEY_API_URL}/transactions"
    headers = {"Authorization": f"Bearer {LUNCHMONEY_API_KEY}"}
    params = {"asset_id": asset_id, "start_date": start_date, "end_date": end_date}

    response = httpx.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("transactions", [])


def send_batch(transactions: list[dict]) -> list[dict]:
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
        logger.info(response.json())
        all_responses.append(response.json())
    return all_responses


def transform_transaction(gocardless_tx: dict, lunchmoney_account_id: int) -> dict:
    logger.debug(f"Transforming transaction: {gocardless_tx}")
    raw_notes = gocardless_tx.get("remittanceInformationUnstructured", "")
    notes = (
        raw_notes
        if "remittanceinformation:" not in raw_notes
        else raw_notes.split("remittanceinformation:")[1].strip()
    )
    parsed = {
        "date": datetime.fromisoformat(gocardless_tx["bookingDate"]).date().isoformat(),
        "amount": f"{float(gocardless_tx['transactionAmount']['amount']):.2f}",
        "currency": (gocardless_tx["transactionAmount"]["currency"]).lower(),
        "payee": gocardless_tx.get(
            "merchantName", gocardless_tx.get("creditorName", "Unknown")
        ).strip(),
        "notes": notes.strip(),
        "asset_id": lunchmoney_account_id,
        "external_id": gocardless_tx["internalTransactionId"],
        "status": "uncleared",
    }
    logger.debug(f"Transformed transaction: {parsed}")
    return parsed


def schedule_sync(token_storage: TokenStorage):
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        lambda: sync_transactions(token_storage),
        trigger=CronTrigger(hour="*/3"),
        id="sync_job",
        replace_existing=True,
    )
