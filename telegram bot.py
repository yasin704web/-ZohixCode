# telegram_bot.py
# راه‌اندازی ربات تلگرام و زمان‌بندی یادآوری‌ها بر اساس store.py
# این ماژول داخل main.py (کنار API) اجرا می‌شه، نه جدا.

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

import config
import store

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=pytz.timezone(config.TIMEZONE))
telegram_app: Application | None = None


async def _send_reminder(chat_id: int, message: str):
    text = f"🔔 {config.USER_NAME}, {message}"
    await telegram_app.bot.send_message(chat_id=chat_id, text=text)


def _job_id(time_str: str) -> str:
    return f"reminder_{time_str}"


def sync_jobs_with_store():
    """زمان‌بندی‌های اسکجولر رو با چیزی که توی store.py هست هماهنگ می‌کنه.
    هر بار که از API یادآوری اضافه/حذف می‌شه، این تابع صدا زده می‌شه."""
    current_reminders = store.list_reminders()
    current_times = {r["time"] for r in current_reminders}

    # حذف job هایی که دیگه توی لیست نیستن
    for job in scheduler.get_jobs():
        time_str = job.id.replace("reminder_", "")
        if time_str not in current_times:
            job.remove()

    # اضافه/آپدیت job برای هر یادآوری فعلی
    for reminder in current_reminders:
        hour, minute = map(int, reminder["time"].split(":"))
        scheduler.add_job(
            _send_reminder,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[config.CHAT_ID, reminder["text"]],
            id=_job_id(reminder["time"]),
            replace_existing=True,
        )
    logger.info("زمان‌بندی یادآوری‌ها هماهنگ شد: %s", sorted(current_times))


# ---------------- دستورهای ربات (اختیاری، برای کنترل از خود تلگرام) ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"سلام {config.USER_NAME} 👋\nربات و داشبورد به هم وصلن. "
        "یادآوری‌ها رو از داشبورد وب مدیریت کن."
    )


async def list_reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminders = store.list_reminders()
    if not reminders:
        await update.message.reply_text("هیچ یادآوری‌ای ثبت نشده.")
        return
    lines = ["📋 یادآوری‌های فعال:"]
    for r in reminders:
        lines.append(f"- {r['time']} : {r['text']}")
    await update.message.reply_text("\n".join(lines))


async def setup_telegram_app():
    """ربات رو می‌سازه، هندلرها رو وصل می‌کنه، و polling رو استارت می‌کنه."""
    global telegram_app
    telegram_app = Application.builder().token(config.BOT_TOKEN).build()

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("list", list_reminders_command))

    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()

    sync_jobs_with_store()
    scheduler.start()
    logger.info("ربات تلگرام و اسکجولر آماده‌ن.")


async def shutdown_telegram_app():
    if telegram_app is not None:
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()
    if scheduler.running:
        scheduler.shutdown()
