import json
import logging
import os
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Tuple

import httpx
from flask.cli import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

project_dir = Path(__file__).parents[2]
load_dotenv(os.path.join(project_dir, ".env"))

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


def extract_rate_limits(headers: httpx.Headers) -> Dict:
    reset_in_mins = int(headers.get("http_x_ratelimit_reset", 0))
    delta = timedelta(minutes=reset_in_mins) if reset_in_mins else timedelta(hours=24)
    reset_timestamp = (datetime.now(timezone.utc) + delta).isoformat()
    rate_limits = {
        "limit": int(headers.get("http_x_ratelimit_limit", 0)),
        "remaining": int(headers.get("http_x_ratelimit_remaining", 0)),
        "reset": reset_timestamp,
    }
    return rate_limits


def load_account_links() -> List[Dict]:
    if not ACCOUNT_LINKS_FILE.exists():
        return []
    with open(ACCOUNT_LINKS_FILE, mode="r") as f:
        content = f.read()
        return json.loads(content)["links"]


def load_sync_status() -> Dict:
    if not SYNC_STATUS_FILE.exists():
        return {}
    with open(SYNC_STATUS_FILE, "r") as f:
        return json.load(f)


def save_sync_status(status: Dict):
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
) -> Tuple[Dict, Dict]:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}"
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
    url = f"{LUNCHMONEY_API_URL}/assets"
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


def get_account_status(account_id: str, access_token: str) -> Dict:
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
    account_links = load_account_links()
    sync_status = load_sync_status()

    if account_id:
        account_links = [
            link for link in account_links if link["gocardlessId"] == account_id
        ]

    access_token = get_gocardless_token(token_storage)

    for link in account_links:
        account_id = link["gocardlessId"]

        # Update sync status
        if account_id not in sync_status:
            sync_status[account_id] = {}

        sync_status[account_id]["isSyncing"] = True
        sync_status[account_id]["lastSyncStatus"] = "pending"
        save_sync_status(sync_status)

        try:
            # Get fresh rate limits before sync
            _, rate_limits = get_gocardless_account_details(account_id, access_token)

            # Perform sync logic here
            # For now, we'll just simulate a successful sync
            sync_status[account_id].update(
                {
                    "lastSync": datetime.now(timezone.utc).isoformat(),
                    "lastSyncStatus": "success",
                    "lastSyncTransactions": 5,  # Example value
                    "isSyncing": False,
                    "rateLimit": rate_limits,
                }
            )
        except Exception as e:
            logger.error(f"Sync failed for account {account_id}: {str(e)}")
            sync_status[account_id].update(
                {
                    "lastSync": datetime.now(timezone.utc).isoformat(),
                    "lastSyncStatus": "error",
                    "isSyncing": False,
                }
            )

        save_sync_status(sync_status)


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
