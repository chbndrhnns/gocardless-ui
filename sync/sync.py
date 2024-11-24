import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
import logging
from typing import List, Dict
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask.cli import load_dotenv

HTTPX_REQUEST_TIMEOUT_IN_S = 30

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

project_dir = Path(__file__).parent
load_dotenv((project_dir.parent / ".env").resolve())

# Configuration
GOCARDLESS_API_URL = "https://bankaccountdata.gocardless.com/api/v2"
GOCARDLESS_SECRET_ID = os.environ.get("VITE_SECRET_ID")
GOCARDLESS_SECRET_KEY = os.environ.get("VITE_SECRET_KEY")
LUNCHMONEY_API_URL = "https://dev.lunchmoney.app/v1"
LUNCHMONEY_API_KEY = os.environ.get("LUNCHMONEY_ACCESS_TOKEN")
ACCOUNT_LINKS_FILE = (
        project_dir.parent / "server" / "data" / "account-links.json"
).resolve()
LAST_SYNC_FILE = project_dir / "last_sync.txt"

# Flask app
app = Flask(__name__)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# In-memory token storage
gocardless_token = None
token_expiry = None


# Load account links
def load_account_links() -> List[Dict]:
    with open(ACCOUNT_LINKS_FILE, "r") as f:
        return json.load(f)["links"]


# Get last sync timestamp
def get_last_sync() -> str:
    if os.path.exists(LAST_SYNC_FILE):
        with open(LAST_SYNC_FILE, "r") as f:
            return f.read().strip()
    return (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()


# Update last sync timestamp
def update_last_sync(timestamp: str):
    with open(LAST_SYNC_FILE, "w") as f:
        f.write(timestamp)


# Get GoCardless access token
def get_gocardless_token() -> str:
    global gocardless_token, token_expiry

    if gocardless_token and token_expiry and datetime.now(timezone.utc) < token_expiry:
        return gocardless_token

    url = f"{GOCARDLESS_API_URL}/token/new/"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "secret_id": GOCARDLESS_SECRET_ID,
        "secret_key": GOCARDLESS_SECRET_KEY
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        token_data = response.json()

        gocardless_token = token_data["access"]
        token_expiry = datetime.now(timezone.utc) + timedelta(seconds=token_data["access_expires"])

        return gocardless_token


# Get GoCardless account name
def get_gocardless_account_name(account_id: str, access_token: str) -> str:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        account_data = response.json()
        return account_data.get("iban", "Unknown Account")


# Get Lunch Money account name
def get_lunchmoney_account_name(account_id: int) -> str:
    url = f"{LUNCHMONEY_API_URL}/assets"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json"
    }

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        accounts = response.json().get("assets", [])
        for account in accounts:
            if account["id"] == account_id:
                return account.get("name", "Unknown Account")
    return "Unknown Account"


# Query GoCardless API for transactions
def get_gocardless_transactions(
        account_id: str, from_date: str, access_token: str
) -> Dict:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"date_from": from_date}

    with httpx.Client(timeout=HTTPX_REQUEST_TIMEOUT_IN_S) as client:
        response = client.get(url, headers=headers, params=params, follow_redirects=True)
        response.raise_for_status()
        return response.json()["transactions"]


# Transform GoCardless transaction to Lunch Money schema
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
        "status": "cleared" if tx_type == "booked" else "pending",
    }


# Send transactions to Lunch Money
def send_to_lunchmoney(transactions: List[Dict]) -> Dict:
    url = f"{LUNCHMONEY_API_URL}/transactions"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"transactions": transactions, "check_for_recurring": True}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()


# Sync transactions for a single account
def sync_account(link: Dict):
    last_sync = get_last_sync()
    from_date = (datetime.fromisoformat(last_sync) - timedelta(days=5)).date().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    all_transactions = []

    access_token = get_gocardless_token()

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
            access_token = get_gocardless_token()
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


# Main sync function
def sync_transactions(account_id=None):
    account_links = load_account_links()
    if account_id:
        account_links = [
            link for link in account_links if link["gocardlessId"] == account_id
        ]

    for link in account_links:
        sync_account(link)


# Schedule sync job
def schedule_sync():
    scheduler.add_job(
        sync_transactions,
        trigger=CronTrigger(
            hour="7-19/3", minute="0"
        ),  # Run every 3 hours from 7 AM to 7 PM
        id="sync_job",
        replace_existing=True,
    )


# Flask routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/accounts")
def get_accounts():
    accounts = load_account_links()
    last_sync = get_last_sync()
    access_token = get_gocardless_token()

    for account in accounts:
        account["gocardlessName"] = get_gocardless_account_name(account["gocardlessId"], access_token)
        account["lunchmoneyName"] = get_lunchmoney_account_name(account["lunchmoneyId"])

    return jsonify({"accounts": accounts, "lastSync": last_sync})


@app.route("/api/sync", methods=["POST"])
def trigger_sync():
    account_id = request.json.get("accountId")
    sync_transactions(account_id)
    return jsonify({"status": "success"})


if __name__ == "__main__":
    schedule_sync()
    app.run(debug=True, port=5001)
