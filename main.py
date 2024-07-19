
from config import Config
from reading import read_sensor, save_reading
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from fastapi import FastAPI

app = FastAPI()
scheduler = AsyncIOScheduler()

@app.get("/sensor")
async def sensor():
    return read_sensor()

@scheduler.scheduled_job('interval', seconds=Config.DATA['read_freq'])
def scheduled_reading():
    save_reading()

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()