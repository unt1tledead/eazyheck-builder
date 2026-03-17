from aiogram import Router
from aiogram.types import Message, FSInputFile
import pyautogui
import tempfile, os

router = Router()

@router.message(lambda m: m.text == "📸 Скриншот")
async def take_screenshot(message: Message):
    await message.answer("📸 Делаю скриншот...")
    path = tempfile.mktemp(suffix=".png")
    pyautogui.screenshot(path)
    await message.answer_photo(FSInputFile(path))
    os.remove(path)
