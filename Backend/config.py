# config.py
# تنظیمات بک‌اند. همه مقادیر حساس از فایل .env خونده می‌شن.

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID_RAW = os.getenv("TELEGRAM_CHAT_ID")
CHAT_ID = int(CHAT_ID_RAW) if CHAT_ID_RAW else None

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN یا TELEGRAM_CHAT_ID تنظیم نشده. "
        "فایل .env.example رو کپی کن به .env و مقادیر واقعی رو بذار."
    )

USER_NAME = os.getenv("USER_NAME", "آقا یاسین")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tehran")

# آدرس فرانت‌اندی که اجازه داره به این API درخواست بزنه (CORS)
# چند تا آدرس رو با کاما جدا کن، مثلاً:
# ALLOWED_ORIGINS=http://localhost:5500,https://yasin-dashboard.vercel.app
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

# فایلی که یادآوری‌ها داخلش ذخیره می‌شن (ساده، بدون نیاز به دیتابیس)
DATA_FILE = os.getenv("DATA_FILE", "reminders.json")
