import logging
import os
from contextlib import asynccontextmanager
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import lunchmoney_api, sync_api, institutions_api, requisitions_api
from .dependencies import get_sync_service

# Load environment variables
load_dotenv()
logging.basicConfig(
    level=os.getenv("BACKEND_LOG_LEVEL"),
    format="%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


async def schedule_sync():
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    logger.info("Starting sync scheduler...")
    sync_service = get_sync_service()

    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(
        sync_service.sync_transactions,
        id="startup_sync_job",
        trigger=CronTrigger(hour="*/5", jitter=120),
        replace_existing=True,
    )
    return scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # noinspection PyUnresolvedReferences
    app.state.scheduler = await schedule_sync()
    yield
    # noinspection PyUnresolvedReferences
    app.state.scheduler.shutdown()


app = FastAPI(title="GoCardless Dashboard API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("BACKEND_CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lunchmoney_api.router, prefix="/api/lunchmoney", tags=["lunchmoney"])
app.include_router(sync_api.router, prefix="/api/sync", tags=["sync"])
app.include_router(
    institutions_api.router, prefix="/api/institutions", tags=["institutions"]
)
app.include_router(
    requisitions_api.router, prefix="/api/requisitions", tags=["requisitions"]
)
