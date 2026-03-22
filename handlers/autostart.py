from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import subprocess, json, winreg

router = Router()

class AutostartState(StatesGroup):
    waiting_num = State()

def get_autostart():
    result = subprocess.run([
        "powershell", "-Command",
        "Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' | ConvertTo-Json"
    ], capture_output=True, text=True, timeout=10)
    try:
        data = json.loads(result.stdout)
        return {k: v for k, v in data.items() if not k.startswith("PS")}
    except Exception:
        return {}

def del_by_index(idx):
    items = get_autostart()
    keys = list(items.keys())
    if idx < 1 or idx > len(keys):
        return None
    name = keys[idx - 1]
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        return name
    except Exception:
        return None

@router.message(lambda m: m.text == "🔐 Автозапуск")
async def autostart_menu(message: Message):
    items = get_autostart()
    text = "🔐 <b>Автозапуск</b>\n\n"
    if items:
        for i, (name, path) in enumerate(items.items(), 1):
            text += f"<code>{i}</code> {name}\n<i>{path[:60]}</i>\n\n"
    else:
        text += "Список пуст"

    kb = None
    if items:
        buttons = []
        for i in range(1, len(items) + 1):
            buttons.append(InlineKeyboardButton(text=f"❌ Удалить {i}", callback_data=f"del_start_{i}", style="danger"))
        rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
        kb = InlineKeyboardMarkup(inline_keyboard=rows)

    await message.answer(text, reply_markup=kb)

@router.callback_query(lambda c: c.data.startswith("del_start_"))
async def del_autostart_cb(callback: CallbackQuery):
    idx = int(callback.data.replace("del_start_", ""))
    name = del_by_index(idx)
    if name:
        await callback.answer(f"✅ {name} удалён")
    else:
        await callback.answer("❌ Не найдено")
    items = get_autostart()
    text = "🔐 <b>Автозапуск</b>\n\n"
    if items:
        for i, (n, path) in enumerate(items.items(), 1):
            text += f"<code>{i}</code> {n}\n<i>{path[:60]}</i>\n\n"
        buttons = []
        for i in range(1, len(items) + 1):
            buttons.append(InlineKeyboardButton(text=f"❌ Удалить {i}", callback_data=f"del_start_{i}", style="danger"))
        rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
        kb = InlineKeyboardMarkup(inline_keyboard=rows)
    else:
        text += "Список пуст"
        kb = None
    await callback.message.edit_text(text, reply_markup=kb)
