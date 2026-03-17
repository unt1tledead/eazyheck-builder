from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import subprocess, sys

router = Router()

power_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔒 Блокировка", callback_data="lock", style="primary"),
     InlineKeyboardButton(text="😴 Сон", callback_data="sleep", style="primary")],
    [InlineKeyboardButton(text="🔁 Перезагрузка", callback_data="reboot", style="danger"),
     InlineKeyboardButton(text="⏻ Выключение", callback_data="shutdown", style="danger")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_power", style="success")]
])

@router.message(lambda m: m.text == "⏻ Питание")
async def power_menu(message: Message):
    await message.answer("⏻ <b>Управление питанием</b>\nВыбери действие:",
                         reply_markup=power_kb, parse_mode="HTML")

@router.callback_query(lambda c: c.data in ["lock", "sleep", "reboot", "shutdown", "cancel_power"])
async def power_action(callback: CallbackQuery):
    action = callback.data
    if action == "cancel_power":
        await callback.message.edit_text("❌ Отменено")
        return

    cmds = {
        "lock": {
            "win32": "rundll32.exe user32.dll,LockWorkStation",
            "linux": "loginctl lock-session",
            "darwin": "osascript -e 'tell application \"System Events\" to keystroke \"q\" using {command down, control down}'"
        },
        "sleep": {
            "win32": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            "linux": "systemctl suspend",
            "darwin": "pmset sleepnow"
        },
        "reboot": {
            "win32": "shutdown /r /t 5",
            "linux": "shutdown -r now",
            "darwin": "shutdown -r now"
        },
        "shutdown": {
            "win32": "shutdown /s /t 5",
            "linux": "shutdown now",
            "darwin": "shutdown -h now"
        }
    }

    platform = sys.platform
    cmd = cmds[action].get(platform) or cmds[action].get("linux")
    labels = {"lock": "🔒 Заблокировано", "sleep": "😴 Уходим в сон",
              "reboot": "🔁 Перезагрузка через 5 сек...", "shutdown": "⏻ Выключение через 5 сек..."}
    await callback.message.edit_text(labels[action])
    subprocess.Popen(cmd, shell=True)
