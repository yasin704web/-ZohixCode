# store.py
# ذخیره‌سازی ساده یادآوری‌ها روی یه فایل JSON — نیازی به دیتابیس جدا نیست.

import json
import os
from threading import Lock

import config

_lock = Lock()

DEFAULT_REMINDERS = [
    {"time": "15:59", "text": "یک دقیقه مونده تا ساعت پست! آماده باش."},
    {"time": "16:00", "text": "الان وقتشه! پست رو منتشر کن."},
]


def _ensure_file():
    if not os.path.exists(config.DATA_FILE):
        with open(config.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_REMINDERS, f, ensure_ascii=False, indent=2)


def list_reminders():
    with _lock:
        _ensure_file()
        with open(config.DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def _save(reminders):
    with open(config.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)


def add_reminder(time_str: str, text: str):
    with _lock:
        _ensure_file()
        reminders = list_reminders()
        reminders = [r for r in reminders if r["time"] != time_str]  # جایگزینی اگه تکراری بود
        reminders.append({"time": time_str, "text": text})
        reminders.sort(key=lambda r: r["time"])
        _save(reminders)
        return reminders


def remove_reminder(time_str: str):
    with _lock:
        _ensure_file()
        reminders = list_reminders()
        reminders = [r for r in reminders if r["time"] != time_str]
        _save(reminders)
        return reminders
