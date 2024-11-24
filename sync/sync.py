import json
import logging
import os
from datetime import datetime, timezone, timedelta
from functools import partial, lru_cache
from pathlib import Path
from typing import List, Dict

import aiofiles
import fastapi
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from flask.cli import load_dotenv
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

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


# FastAPI app
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory=project_dir/"static"), name="static")

# Templates
templates = Jinja2Templates(directory=project_dir/"templates")

# Scheduler
scheduler = AsyncIOScheduler()
scheduler.start()


# Token Storage Class
class TokenStorage:
    def __init__(self):
        self.gocardless_token = None
        self.token_expiry = None

@lru_cache
def get_token_storage() -> TokenStorage:
    return TokenStorage()

# Load account links
async def load_account_links() -> List[Dict]:
    async with aiofiles.open(ACCOUNT_LINKS_FILE, mode="r") as f:
        content = await f.read()
        return json.loads(content)["links"]


# Get last sync timestamp
async def get_last_sync() -> str:
    if os.path.exists(LAST_SYNC_FILE):
        async with aiofiles.open(LAST_SYNC_FILE, "r") as f:
            return (await f.read()).strip()
    return (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()


# Update last sync timestamp
async def update_last_sync(timestamp: str):
    async with aiofiles.open(LAST_SYNC_FILE, "w") as f:
        await f.write(timestamp)


# Get GoCardless access token
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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        token_data = response.json()

        token_storage.gocardless_token = token_data["access"]
        token_storage.token_expiry = datetime.now(timezone.utc) + timedelta(
            seconds=token_data["access_expires"]
        )

        return token_storage.gocardless_token


# Get GoCardless account name
async def get_gocardless_account_name(account_id: str, access_token: str) -> str:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        account_data = response.json()
        return account_data.get("iban", "Unknown Account")


# Get Lunch Money account name
def get_lunchmoney_account_name(account_id: int) -> str:
    url = f"{LUNCHMONEY_API_URL}/assets"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json",
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
async def get_gocardless_transactions(
    account_id: str, from_date: str, access_token: str
) -> Dict:
    url = f"{GOCARDLESS_API_URL}/accounts/{account_id}/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"date_from": from_date}

    async with httpx.AsyncClient(timeout=HTTPX_REQUEST_TIMEOUT_IN_S) as client:
        response = await client.get(
            url, headers=headers, params=params, follow_redirects=True
        )
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
        "status": "uncleared",
        # https://discord.com/channels/842337014556262411/1134594318414389258/1310001938795991092
        # "status": "cleared" if tx_type == "booked" else "pending",
    }


# Send transactions to Lunch Money
async def send_to_lunchmoney(transactions: List[Dict]) -> Dict:
    url = f"{LUNCHMONEY_API_URL}/transactions"
    headers = {
        "Authorization": f"Bearer {LUNCHMONEY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"transactions": transactions, "check_for_recurring": True}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()


# Sync transactions for a single account
async def sync_account(token_storage: TokenStorage, link: Dict):
    last_sync = await get_last_sync()
    from_date = (
        (datetime.fromisoformat(last_sync) - timedelta(days=5)).date().isoformat()
    )
    now = datetime.now(timezone.utc).isoformat()
    all_transactions = []

    access_token = await get_gocardless_token(token_storage)

    logging.info(f"Fetching transactions for account {link['gocardlessId']}")
    try:
        gocardless_data = await get_gocardless_transactions(
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
            access_token = await get_gocardless_token(token_storage)
            gocardless_data = await get_gocardless_transactions(
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
            result = await send_to_lunchmoney(all_transactions)
            logging.info(
                f"Synced {len(all_transactions)} transactions for account {link['gocardlessId']}. Lunch Money response: {result}"
            )
        except Exception as e:
            logging.error(
                f"Error sending transactions to Lunch Money for account {link['gocardlessId']}: {str(e)}"
            )
    else:
        logging.info(f"No new transactions to sync for account {link['gocardlessId']}.")

    await update_last_sync(now)


# Main sync function
async def sync_transactions(token_storage: TokenStorage, account_id=None):
    account_links = await load_account_links()
    if account_id:
        account_links = [
            link for link in account_links if link["gocardlessId"] == account_id
        ]

    for link in account_links:
        await sync_account(token_storage, link)


# Schedule sync job
def schedule_sync(token_storage: TokenStorage):
    scheduler.add_job(
        partial(sync_transactions, get_token_storage()),
        trigger=CronTrigger(
            hour="7-19/3", minute="0"
        ),  # Run every 3 hours from 7 AM to 7 PM
        id="sync_job",
        job_executor="async",
        replace_existing=True,
    )


# FastAPI routes
@app.get("/")
async def index(request: fastapi.Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    return response


@app.get("/api/accounts")
async def get_accounts(token_storage=fastapi.Depends(get_token_storage)):
    accounts = await load_account_links()
    last_sync = await get_last_sync()
    access_token = await get_gocardless_token(token_storage)

    for account in accounts:
        account["gocardlessName"] = await get_gocardless_account_name(
            account["gocardlessId"], access_token
        )
        account["lunchmoneyName"] = get_lunchmoney_account_name(account["lunchmoneyId"])

    return JSONResponse(content={"accounts": accounts, "lastSync": last_sync})


class SyncRequest(BaseModel):
    accountId: str


@app.post("/api/sync")
async def trigger_sync(sync_request: SyncRequest, token_storage=fastapi.Depends(get_token_storage)):
    await sync_transactions(token_storage, sync_request.accountId)
    return JSONResponse(content={"status": "success"})


if __name__ == "__main__":
    schedule_sync(get_token_storage())
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)
