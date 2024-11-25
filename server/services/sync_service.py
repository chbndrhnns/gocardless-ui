import json
import logging
import os
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pathlib import Path
from typing import List, Dict

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
LAST_SYNC_FILE = Path(project_dir / "server" / "data" / "last-sync.txt")


class TokenStorage:
    def __init__(self):
        self.gocardless_token = None
        self.token_expiry = None


@lru_cache
def get_token_storage() -> TokenStorage:
    return TokenStorage()


def load_account_links() -> List[Dict]:
    with open(ACCOUNT_LINKS_FILE, mode="r") as f:
        content = f.read()
        return json.loads(content)["links"]


def get_last_sync() -> str:
    if os.path.isfile(LAST_SYNC_FILE):
        with open(LAST_SYNC_FILE, "r") as f:
            return f.read().strip()
    return (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()


def update_last_sync(timestamp: str):
    with open(LAST_SYNC_FILE, "w") as f:
        f.write(timestamp)


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

    response = httpx.post(url, headers=headers, json=data)
    response.raise_for_status()
    token_data = response.json()

    token_storage.gocardless_token = token_data["access"]
    token_storage.token_expiry = datetime.now(timezone.utc) + timedelta(
        seconds=token_data["access_expires"]
    )

    return token_storage.gocardless_token


def get_gocardless_account_name(account_id: str, access_token: str) -> str:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.raise_for_status()
    account_data = response.json()
    return account_data.get("iban", "Unknown Account")


def get_lunchmoney_account_name(account_id: int) -> str:
    url = f"{LUNCHMONEY_API_URL}/assets"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json",
    }

    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.raise_for_status()
    accounts = response.json().get("assets", [])
    for account in accounts:
        if account["id"] == account_id:
            return account.get("name", "Unknown Account")
    return "Unknown Account"


def get_gocardless_transactions(
    account_id: str, from_date: str, access_token: str
) -> Dict:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"date_from": from_date}

    response = httpx.get(url, headers=headers, params=params, follow_redirects=True)
    response.raise_for_status()
    return response.json()["transactions"]


def transform_transaction(
    gocardless_tx: Dict, lunchmoney_account_id: int, tx_type: str
) -> Dict:
    return {
        "date": datetime.fromisoformat(gocardless_tx["bookingDate"]).date().isoformat(),
        "amount": f"{abs(float(gocardless_tx['transactionAmount']['amount'])):.4f}",
        "currency": (gocardless_tx["transactionAmount"]["currency"]).lower(),
        "payee": gocardless_tx.get(
            "merchantName", gocardless_tx.get("debtorName", "Unknown")
        ),
        "notes": gocardless_tx.get("remittanceInformationUnstructured", ""),
        "account_id": lunchmoney_account_id,
        "external_id": gocardless_tx["transactionId"],
        "status": "uncleared",
    }


def send_to_lunchmoney(transactions: List[Dict]) -> Dict:
    url = f"{LUNCHMONEY_API_URL}/transactions"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"transactions": transactions, "check_for_recurring": True}

    response = httpx.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def sync_account(token_storage: TokenStorage, link: Dict):
    last_sync = get_last_sync()
    from_date = (
        (datetime.fromisoformat(last_sync) - timedelta(days=5)).date().isoformat()
    )
    now = datetime.now(timezone.utc).isoformat()
    all_transactions = []

    access_token = get_gocardless_token(token_storage)

    logging.info(f"Fetching transactions for account {link['gocardlessId']}")
    try:
        gocardless_data = get_gocardless_transactions(
            link["gocardlessId"], from_date, access_token
        )

        for tx_type in ["booked", "pending"]:
            transformed_transactions = [
                transform_transaction(tx, link["lunchmoneyId"], tx_type)
                for tx in gocardless_data.get(tx_type, [])
            ]
            all_transactions.extend(transformed_transactions)

        logging.info(
            f"Fetched {len(transformed_transactions)} transactions for account {link['gocardlessId']}"
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            logging.warning("Access token expired. Refreshing token and retrying.")
            access_token = get_gocardless_token(token_storage)
            gocardless_data = get_gocardless_transactions(
                link["gocardlessId"], from_date, access_token
            )
            for tx_type in ["booked", "pending"]:
                transformed_transactions = [
                    transform_transaction(tx, link["lunchmoneyId"], tx_type)
                    for tx in gocardless_data.get(tx_type, [])
                ]
                all_transactions.extend(transformed_transactions)
            logging.info(
                f"Fetched {len(transformed_transactions)} transactions for account {link['gocardlessId']} after token refresh"
            )
        else:
            logging.error(
                f"Error fetching transactions for account {link['gocardlessId']}: {str(e)}"
            )
    except Exception as e:
        logging.error(
            f"Error fetching transactions for account {link['gocardlessId']}: {str(e)}"
        )

    if all_transactions:
        try:
            result = send_to_lunchmoney(all_transactions)
            logging.info(
                f"Synced {len(all_transactions)} transactions for account {link['gocardlessId']}. Lunch Money response: {result}"
            )
        except Exception as e:
            logging.error(
                f"Error sending transactions to Lunch Money for account {link['gocardlessId']}: {str(e)}"
            )
    else:
        logging.info(f"No new transactions to sync for account {link['gocardlessId']}.")

    update_last_sync(now)


def sync_transactions(token_storage: TokenStorage, account_id=None):
    account_links = load_account_links()
    if account_id:
        account_links = [
            link for link in account_links if link["gocardlessId"] == account_id
        ]

    for link in account_links:
        sync_account(token_storage, link)


def schedule_sync(token_storage: TokenStorage):
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        lambda: sync_transactions(token_storage),
        trigger=CronTrigger(hour="7-19/3", minute="0"),
        id="sync_job",
        replace_existing=True,
    )
