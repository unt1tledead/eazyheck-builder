from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import subprocess

router = Router()

class AutostartState(StatesGroup):
    waiting_name = State()

def get_autostart():
    result = subprocess.run([
        "powershell", "-Command",
        "Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' | ConvertTo-Json"
    ], capture_output=True, text=True, timeout=10)
    import json
    try:
        data = json.loads(result.stdout)
        return {k: v for k, v in data.items() if not k.startswith("PS")}
    except Exception:
        return {}

@router.message(lambda m: m.text == "🔐 Автозапуск")
async def autostart_menu(message: Message):
    items = get_autostart()
    text = "🔐 <b>Автозапуск</b>\n\n"
    if items:
        for i, (name, path) in enumerate(items.items(), 1):
            text += f"<code>{i}</code> {name}\n<i>{path[:60]}</i>\n\n"
        text += "/delstart [имя] — удалить из автозапуска"
    else:
        text += "Список пуст"
    await message.answer(text)

@router.message(F.text.startswith("/delstart"))
async def del_autostart(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи имя: /delstart Chrome")
        return
    name = parts[1].strip()
    try:
        subprocess.run([
            "powershell", "-Command",
            f"Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name '{name}'"
        ], capture_output=True, text=True, timeout=10)
        await message.answer(f"✅ {name} удалён из автозапуска")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
