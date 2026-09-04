# main.py
# API اصلی بک‌اند — این فایل رو اجرا می‌کنیم (با uvicorn)
# هم API میده به فرانت‌اند، هم ربات تلگرام رو کنار خودش نگه می‌داره.

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
import store
import telegram_bot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_bot.setup_telegram_app()
    yield
    await telegram_bot.shutdown_telegram_app()


app = FastAPI(title="Yasin Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReminderIn(BaseModel):
    time: str  # فرمت "HH:MM"
    text: str


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/reminders")
def get_reminders():
    return store.list_reminders()


@app.post("/api/reminders")
def create_reminder(reminder: ReminderIn):
    if len(reminder.time) != 5 or reminder.time[2] != ":":
        raise HTTPException(status_code=400, detail="فرمت ساعت باید HH:MM باشه")
    if not reminder.text.strip():
        raise HTTPException(status_code=400, detail="متن یادآوری نمی‌تونه خالی باشه")

    reminders = store.add_reminder(reminder.time, reminder.text.strip())
    telegram_bot.sync_jobs_with_store()
    return reminders


@app.delete("/api/reminders/{time_str}")
def delete_reminder(time_str: str):
    reminders = store.remove_reminder(time_str)
    telegram_bot.sync_jobs_with_store()
    return reminders


@app.get("/api/status")
def status():
    return {
        "telegram": True,
        "instagram": False,
        "youtube": False,
        "tiktok": False,
    }
