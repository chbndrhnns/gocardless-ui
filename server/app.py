import logging
import os
from contextlib import asynccontextmanager

from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.services.sync_service import (
    TokenStorage,
    sync_transactions,
    get_token_storage,
)
from .routes import (
    accounts_routes,
    auth_routes,
    institutions_routes,
    lunchmoney_routes,
    requisitions_routes,
    sync_routes,
)

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


async def schedule_sync(token_storage: TokenStorage):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    logger.info("Starting sync scheduler...")

    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(
        sync_transactions,
        args=(token_storage,),
        id="startup_sync_job",
        trigger=CronTrigger(hour="*/5", jitter=120),
        replace_existing=True,
    )
    return scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.scheduler = await schedule_sync(get_token_storage())
    yield
    app.state.scheduler.shutdown()


app = FastAPI(title="GoCardless Dashboard API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(
    requisitions_routes.router, prefix="/api/requisitions", tags=["requisitions"]
)
app.include_router(
    institutions_routes.router, prefix="/api/institutions", tags=["institutions"]
)
app.include_router(accounts_routes.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(
    lunchmoney_routes.router, prefix="/api/lunchmoney", tags=["lunchmoney"]
)
app.include_router(sync_routes.router, prefix="/api/sync", tags=["sync"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("BACKEND_PORT", 4000))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port, reload=True)
