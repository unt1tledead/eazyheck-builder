from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import pyautogui

router = Router()

media_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏮ Пред", callback_data="med_prev", style="primary"),
     InlineKeyboardButton(text="⏯ Пауза", callback_data="med_play", style="success"),
     InlineKeyboardButton(text="⏭ След", callback_data="med_next", style="primary")],
    [InlineKeyboardButton(text="🔇 Mute", callback_data="med_mute", style="danger"),
     InlineKeyboardButton(text="🔉 -5%", callback_data="med_vdown", style="primary"),
     InlineKeyboardButton(text="🔊 +5%", callback_data="med_vup", style="primary")],
])

@router.message(lambda m: m.text == "🎵 Медиа")
async def media_menu(message: Message):
    await message.answer("🎵 <b>Управление медиа</b>", reply_markup=media_kb)

@router.callback_query(lambda c: c.data.startswith("med_"))
async def media_action(callback: CallbackQuery):
    actions = {
        "med_prev": ("prevtrack", "⏮ Предыдущий"),
        "med_play": ("playpause", "⏯ Пауза/Воспроизведение"),
        "med_next": ("nexttrack", "⏭ Следующий"),
        "med_mute": ("volumemute", "🔇 Mute"),
        "med_vdown": ("volumedown", "🔉 -5%"),
        "med_vup": ("volumeup", "🔊 +5%"),
    }
    key, label = actions.get(callback.data, (None, "?"))
    if key:
        pyautogui.press(key)
    await callback.answer(label)
