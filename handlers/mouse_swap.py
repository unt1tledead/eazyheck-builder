from aiogram import Router
from aiogram.types import Message
import ctypes, sys

router = Router()
swapped = {"active": False}

@router.message(lambda m: m.text == "🖱 Поменять кнопки мыши")
async def swap_mouse(message: Message):
    if sys.platform != "win32":
        await message.answer("❌ Только Windows")
        return
    if swapped["active"]:
        ctypes.windll.user32.SwapMouseButton(False)
        swapped["active"] = False
        await message.answer("✅ Кнопки мыши возвращены")
    else:
        ctypes.windll.user32.SwapMouseButton(True)
        swapped["active"] = True
        await message.answer("😈 ЛКМ и ПКМ поменяны местами!\nНажми снова чтобы вернуть")
