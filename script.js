// script.js
// منطق داشبورد: ساعت زنده، شمارش‌معکوس تا یادآوری بعدی، افزودن/حذف یادآوری
// نکته: این نسخه فرانت‌اند مستقله و به بک‌اند/ربات تلگرام وصل نیست.
// دیتا فقط توی حافظه مرورگره و با رفرش صفحه به حالت اولیه برمی‌گرده.

let reminders = [
  { time: "15:59", text: "یک دقیقه مونده تا ساعت پست! آماده باش." },
  { time: "16:00", text: "الان وقتشه! پست رو منتشر کن." },
];

const reminderListEl = document.getElementById("reminderList");
const reminderCountEl = document.getElementById("reminderCount");
const nextReminderTextEl = document.getElementById("nextReminderText");
const countdownEl = document.getElementById("countdown");
const liveClockEl = document.getElementById("liveClock");
const addForm = document.getElementById("addForm");
const timeInput = document.getElementById("timeInput");
const textInput = document.getElementById("textInput");

function pad(n) {
  return String(n).padStart(2, "0");
}

function renderReminders() {
  reminderListEl.innerHTML = "";
  reminderCountEl.textContent = reminders.length;

  if (reminders.length === 0) {
    reminderListEl.innerHTML = `<li class="empty-state">هیچ یادآوری‌ای ثبت نشده.</li>`;
    return;
  }

  const sorted = [...reminders].sort((a, b) => a.time.localeCompare(b.time));

  sorted.forEach((r) => {
    const li = document.createElement("li");
    li.className = "reminder-item";
    li.innerHTML = `
      <span class="reminder-time">${r.time}</span>
      <span class="reminder-text">${escapeHtml(r.text)}</span>
      <button class="reminder-remove" aria-label="حذف" data-time="${r.time}">×</button>
    `;
    reminderListEl.appendChild(li);
  });

  reminderListEl.querySelectorAll(".reminder-remove").forEach((btn) => {
    btn.addEventListener("click", () => {
      const t = btn.getAttribute("data-time");
      reminders = reminders.filter((r) => r.time !== t);
      renderReminders();
      updateHero();
    });
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function getNextReminder() {
  const now = new Date();
  const nowMinutes = now.getHours() * 60 + now.getMinutes();

  const withMinutes = reminders.map((r) => {
    const [h, m] = r.time.split(":").map(Number);
    return { ...r, minutes: h * 60 + m };
  });

  let upcoming = withMinutes
    .filter((r) => r.minutes >= nowMinutes)
    .sort((a, b) => a.minutes - b.minutes)[0];

  if (!upcoming && withMinutes.length > 0) {
    // چیزی امروز نمونده، برو سراغ اولین یادآوری فردا
    upcoming = [...withMinutes].sort((a, b) => a.minutes - b.minutes)[0];
  }

  return upcoming || null;
}

function updateHero() {
  const next = getNextReminder();

  if (!next) {
    nextReminderTextEl.textContent = "یادآوری‌ای ثبت نشده";
    countdownEl.textContent = "--:--:--";
    return;
  }

  nextReminderTextEl.textContent = next.text;

  const now = new Date();
  const target = new Date();
  target.setHours(Math.floor(next.minutes / 60), next.minutes % 60, 0, 0);

  if (target < now) {
    target.setDate(target.getDate() + 1);
  }

  const diffMs = target - now;
  const diffSec = Math.floor(diffMs / 1000);
  const h = Math.floor(diffSec / 3600);
  const m = Math.floor((diffSec % 3600) / 60);
  const s = diffSec % 60;

  countdownEl.textContent = `${pad(h)}:${pad(m)}:${pad(s)}`;
}

function updateClock() {
  const now = new Date();
  liveClockEl.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  updateHero();
}

addForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const time = timeInput.value;
  const text = textInput.value.trim();
  if (!time || !text) return;

  reminders.push({ time, text });
  renderReminders();
  updateHero();
  addForm.reset();
});

renderReminders();
updateClock();
setInterval(updateClock, 1000);
