from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pyperclip

router = Router()

class ClipState(StatesGroup):
    waiting_set = State()

clip_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Получить", callback_data="clip_get", style="primary"),
     InlineKeyboardButton(text="✏️ Вставить", callback_data="clip_set", style="success")]
])

@router.message(lambda m: m.text == "📋 Буфер")
async def clipboard_menu(message: Message):
    await message.answer("📋 <b>Буфер обмена</b>", reply_markup=clip_kb, parse_mode="HTML")

@router.callback_query(lambda c: c.data == "clip_get")
async def get_clipboard(callback: CallbackQuery):
    try:
        text = pyperclip.paste()
        if text:
            await callback.message.answer(f"📋 Буфер обмена:\n<code>{text[:2000]}</code>", parse_mode="HTML")
        else:
            await callback.message.answer("📋 Буфер пустой")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
    await callback.answer()

@router.callback_query(lambda c: c.data == "clip_set")
async def ask_clipboard(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи текст для буфера обмена:")
    await state.set_state(ClipState.waiting_set)
    await callback.answer()

@router.message(ClipState.waiting_set)
async def set_clipboard(message: Message, state: FSMContext):
    await state.clear()
    try:
        pyperclip.copy(message.text)
        await message.answer("✅ Текст скопирован в буфер!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
