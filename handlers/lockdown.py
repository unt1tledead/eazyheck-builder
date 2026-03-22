from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pynput import mouse as pmouse, keyboard as pkeyboard
import threading

router = Router()

lock_state = {"mouse": False, "keyboard": False}
listeners = {"mouse": None, "keyboard": None}

def build_kb():
    m = "🟢 Мышь — заблокирована" if lock_state["mouse"] else "⚫️ Мышь — свободна"
    k = "🟢 Клавиатура — заблокирована" if lock_state["keyboard"] else "⚫️ Клавиатура — свободна"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m, callback_data="lock_mouse")],
        [InlineKeyboardButton(text=k, callback_data="lock_keyboard")],
    ])

def start_mouse_block():
    def on_move(x, y): return False
    def on_click(x, y, btn, pressed): return False
    def on_scroll(x, y, dx, dy): return False
    listeners["mouse"] = pmouse.Listener(
        on_move=on_move, on_click=on_click, on_scroll=on_scroll,
        suppress=True
    )
    listeners["mouse"].start()

def stop_mouse_block():
    if listeners["mouse"]:
        listeners["mouse"].stop()
        listeners["mouse"] = None

def start_keyboard_block():
    def on_press(key): return False
    def on_release(key): return False
    listeners["keyboard"] = pkeyboard.Listener(
        on_press=on_press, on_release=on_release,
        suppress=True
    )
    listeners["keyboard"].start()

def stop_keyboard_block():
    if listeners["keyboard"]:
        listeners["keyboard"].stop()
        listeners["keyboard"] = None

@router.message(lambda m: m.text == "🔒 Блокировка")
async def lockdown_menu(message: Message):
    await message.answer("🔒 <b>Блокировка ввода</b>", reply_markup=build_kb())

@router.callback_query(lambda c: c.data == "lock_mouse")
async def toggle_mouse(callback: CallbackQuery):
    lock_state["mouse"] = not lock_state["mouse"]
    if lock_state["mouse"]:
        threading.Thread(target=start_mouse_block, daemon=True).start()
        await callback.answer("🟢 Мышь заблокирована")
    else:
        stop_mouse_block()
        await callback.answer("⚫️ Мышь разблокирована")
    await callback.message.edit_reply_markup(reply_markup=build_kb())

@router.callback_query(lambda c: c.data == "lock_keyboard")
async def toggle_keyboard(callback: CallbackQuery):
    lock_state["keyboard"] = not lock_state["keyboard"]
    if lock_state["keyboard"]:
        threading.Thread(target=start_keyboard_block, daemon=True).start()
        await callback.answer("🟢 Клавиатура заблокирована")
    else:
        stop_keyboard_block()
        await callback.answer("⚫️ Клавиатура разблокирована")
    await callback.message.edit_reply_markup(reply_markup=build_kb())
