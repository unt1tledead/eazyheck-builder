from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os, sqlite3, shutil, tempfile
from datetime import datetime

router = Router()

BROWSERS = {
    "Chrome": os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History"),
    "Edge": os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\History"),
    "Firefox": None,
}

def get_chrome_history(path, limit=20):
    if not os.path.exists(path):
        return []
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2(path, tmp)
    try:
        conn = sqlite3.connect(tmp)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        result = []
        for url, title, visit_time in rows:
            ts = datetime(1601, 1, 1) if visit_time == 0 else datetime.fromtimestamp(
                (visit_time - 11644473600 * 10**7) / 10**7
            )
            result.append((title or url[:50], url, ts.strftime("%d.%m %H:%M")))
        return result
    except Exception:
        return []
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

browser_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔵 Chrome", callback_data="hist_chrome", style="primary"),
     InlineKeyboardButton(text="🔵 Edge", callback_data="hist_edge", style="primary")],
])

@router.message(lambda m: m.text == "🌐 История браузера")
async def browser_menu(message: Message):
    await message.answer("🌐 <b>История браузера</b>\nВыбери браузер:", reply_markup=browser_kb)

@router.callback_query(lambda c: c.data.startswith("hist_"))
async def show_history(callback: CallbackQuery):
    browser = callback.data.split("_")[1]
    paths = {
        "chrome": BROWSERS["Chrome"],
        "edge": BROWSERS["Edge"],
    }
    path = paths.get(browser)
    await callback.answer()
    if not path:
        await callback.message.answer("❌ Браузер не найден")
        return
    await callback.message.answer("⏳ Читаю историю...")
    history = get_chrome_history(path)
    if not history:
        await callback.message.answer("❌ История пуста или браузер не установлен")
        return
    text = f"🌐 <b>История {'Chrome' if browser == 'chrome' else 'Edge'}</b>\n\n"
    for title, url, ts in history[:20]:
        title = title[:40] if title else "без названия"
        text += f"<code>{ts}</code> {title}\n"
    await callback.message.answer(text)
