from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pyautogui
import pyperclip

router = Router()

class MouseState(StatesGroup):
    waiting_type = State()
    waiting_key = State()

mouse_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬆️", callback_data="m_up"),
     InlineKeyboardButton(text="⬇️", callback_data="m_down"),
     InlineKeyboardButton(text="⬅️", callback_data="m_left"),
     InlineKeyboardButton(text="➡️", callback_data="m_right")],
    [InlineKeyboardButton(text="🖱 Клик", callback_data="m_click"),
     InlineKeyboardButton(text="🖱 ПКМ", callback_data="m_rclick"),
     InlineKeyboardButton(text="🖱 Двойной", callback_data="m_dclick")],
    [InlineKeyboardButton(text="⌨️ Нажать клавишу", callback_data="m_key"),
     InlineKeyboardButton(text="✏️ Написать текст", callback_data="m_type")],
])

@router.message(lambda m: m.text == "🖱 Мышь/Клава")
async def mouse_menu(message: Message):
    await message.answer("🖱 Управление мышью и клавиатурой:", reply_markup=mouse_kb)

@router.callback_query(lambda c: c.data.startswith("m_"))
async def mouse_action(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    step = 50
    if action == "m_up":
        pyautogui.move(0, -step)
        await callback.answer("⬆️")
    elif action == "m_down":
        pyautogui.move(0, step)
        await callback.answer("⬇️")
    elif action == "m_left":
        pyautogui.move(-step, 0)
        await callback.answer("⬅️")
    elif action == "m_right":
        pyautogui.move(step, 0)
        await callback.answer("➡️")
    elif action == "m_click":
        pyautogui.click()
        await callback.answer("🖱 Клик")
    elif action == "m_rclick":
        pyautogui.rightClick()
        await callback.answer("🖱 ПКМ")
    elif action == "m_dclick":
        pyautogui.doubleClick()
        await callback.answer("🖱 Двойной клик")
    elif action == "m_key":
        await callback.message.answer("Введи клавишу (enter, space, esc, win, tab...):")
        await state.set_state(MouseState.waiting_key)
        await callback.answer()
    elif action == "m_type":
        await callback.message.answer("Введи текст для печати:")
        await state.set_state(MouseState.waiting_type)
        await callback.answer()

@router.message(MouseState.waiting_key)
async def press_key(message: Message, state: FSMContext):
    await state.clear()
    try:
        pyautogui.press(message.text.strip())
        await message.answer(f"✅ Нажато: {message.text.strip()}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(MouseState.waiting_type)
async def type_text(message: Message, state: FSMContext):
    await state.clear()
    try:
        pyperclip.copy(message.text)
        pyautogui.hotkey("ctrl", "v")
        await message.answer("✅ Напечатано")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
