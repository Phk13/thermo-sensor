from contextlib import asynccontextmanager
from config import Config
from reading import read_sensor, save_reading
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        scheduler.start()
        logger.info("Scheduler started successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise
    finally:
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully")


app = FastAPI(title="Thermo Sensor API", lifespan=lifespan)
scheduler = AsyncIOScheduler()

@app.get("/sensor")
async def sensor():
    """Get current sensor reading."""
    try:
        return read_sensor()
    except Exception as e:
        logger.error(f"Error reading sensor: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to read sensor"}
        )

@scheduler.scheduled_job('interval', seconds=Config.DATA['read_freq'])
async def scheduled_reading():
    """Scheduled task to read and save sensor data."""
    await save_reading()

