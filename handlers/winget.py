from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import subprocess, asyncio

router = Router()

class WingetState(StatesGroup):
    waiting_install = State()
    waiting_remove = State()

@router.message(lambda m: m.text == "📦 Программы")
async def winget_menu(message: Message):
    await message.answer(
        "📦 <b>Менеджер программ (winget)</b>\n\n"
        "/install [название] — установить\n"
        "/uninstall [название] — удалить\n"
        "/winlist — список установленных"
    )

@router.message(F.text.startswith("/install"))
async def install_app(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи название: /install vlc")
        return
    name = parts[1].strip()
    msg = await message.answer(f"📦 Устанавливаю {name}...")
    try:
        result = await asyncio.create_subprocess_shell(
            f'winget install --silent --accept-source-agreements --accept-package-agreements "{name}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=120)
        out = (stdout + stderr).decode("utf-8", errors="ignore")
        if "успешно" in out.lower() or "successfully" in out.lower():
            await msg.edit_text(f"✅ {name} установлен")
        else:
            lines = [l for l in out.split("\n") if l.strip()][-3:]
            await msg.edit_text(f"⚠️ Результат:\n<code>{chr(10).join(lines)}</code>")
    except asyncio.TimeoutError:
        await msg.edit_text("⏱ Превышено время ожидания (2 мин)")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

@router.message(F.text.startswith("/uninstall"))
async def uninstall_app(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи название: /uninstall vlc")
        return
    name = parts[1].strip()
    msg = await message.answer(f"🗑 Удаляю {name}...")
    try:
        result = await asyncio.create_subprocess_shell(
            f'winget uninstall --silent "{name}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=120)
        out = (stdout + stderr).decode("utf-8", errors="ignore")
        await msg.edit_text(f"✅ {name} удалён" if "успешно" in out.lower() or "successfully" in out.lower() else f"⚠️ <code>{out[-300:]}</code>")
    except asyncio.TimeoutError:
        await msg.edit_text("⏱ Превышено время ожидания")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

@router.message(lambda m: m.text == "/winlist")
async def list_apps(message: Message):
    msg = await message.answer("📋 Загружаю список...")
    try:
        result = await asyncio.create_subprocess_shell(
            "winget list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(result.communicate(), timeout=30)
        out = stdout.decode("utf-8", errors="ignore")
        lines = [l for l in out.split("\n") if l.strip() and not l.startswith("-")][:40]
        text = "<code>" + "\n".join(lines) + "</code>"
        if len(text) > 4000:
            text = text[:4000] + "...</code>"
        await msg.edit_text(text)
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")
