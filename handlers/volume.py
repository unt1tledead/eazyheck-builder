from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import subprocess, sys

router = Router()

def vol_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔇 Mute", callback_data="vol_mute", style="danger"),
         InlineKeyboardButton(text="🔉 -10%", callback_data="vol_down", style="primary"),
         InlineKeyboardButton(text="🔊 +10%", callback_data="vol_up", style="success")],
    ])

def set_volume_win(action):
    script = {
        "vol_up": "(New-Object -com Shell.Application).SendKeys([char]175)*2",
        "vol_down": "(New-Object -com Shell.Application).SendKeys([char]174)*2",
        "vol_mute": "(New-Object -com Shell.Application).SendKeys([char]173)",
    }
    subprocess.Popen(["powershell", "-Command", script[action]])

def set_volume_linux(action):
    cmds = {
        "vol_up": "amixer -D pulse sset Master 10%+",
        "vol_down": "amixer -D pulse sset Master 10%-",
        "vol_mute": "amixer -D pulse sset Master toggle",
    }
    subprocess.Popen(cmds[action], shell=True)

@router.message(lambda m: m.text == "🔊 Громкость")
async def volume_menu(message: Message):
    await message.answer("🔊 <b>Управление громкостью</b>",
                         reply_markup=vol_kb(), parse_mode="HTML")

@router.callback_query(lambda c: c.data.startswith("vol_"))
async def volume_action(callback: CallbackQuery):
    action = callback.data
    if sys.platform == "win32":
        set_volume_win(action)
    else:
        set_volume_linux(action)
    labels = {"vol_up": "🔊 +10%", "vol_down": "🔉 -10%", "vol_mute": "🔇 Mute toggle"}
    await callback.answer(labels.get(action, "OK"))
