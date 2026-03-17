from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import webbrowser

router = Router()

class UrlState(StatesGroup):
    waiting = State()

@router.message(lambda m: m.text == "🌐 Открыть URL")
async def ask_url(message: Message, state: FSMContext):
    await message.answer("Введи URL:")
    await state.set_state(UrlState.waiting)

@router.message(UrlState.waiting)
async def open_url(message: Message, state: FSMContext):
    await state.clear()
    url = message.text
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    await message.answer(f"✅ Открыто: {url}")
