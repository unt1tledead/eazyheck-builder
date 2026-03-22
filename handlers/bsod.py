from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import ctypes, sys

router = Router()

bsod_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💥 Да, вызвать BSOD", callback_data="bsod_confirm", style="danger"),
     InlineKeyboardButton(text="❌ Отмена", callback_data="bsod_cancel", style="success")]
])

@router.message(lambda m: m.text == "💥 BSOD")
async def bsod_warn(message: Message):
    await message.answer(
        "💥 <b>BSOD</b>\n\n"
        "⚠️ Это вызовет синий экран смерти и немедленную перезагрузку ПК.\n"
        "Все несохранённые данные будут потеряны.\n\n"
        "Уверен?",
        reply_markup=bsod_kb
    )

@router.callback_query(lambda c: c.data == "bsod_cancel")
async def bsod_cancel(callback: CallbackQuery):
    await callback.message.edit_text("✅ Отменено.")
    await callback.answer()

@router.callback_query(lambda c: c.data == "bsod_confirm")
async def bsod_execute(callback: CallbackQuery):
    if sys.platform != "win32":
        await callback.answer("❌ Только Windows")
        return
    await callback.message.edit_text("💥 Инициирую BSOD...")
    await callback.answer()
    try:
        ntdll = ctypes.windll.ntdll
        prev = ctypes.c_bool()
        ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(prev))
        ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, None, 6, ctypes.byref(ctypes.c_ulong()))
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
