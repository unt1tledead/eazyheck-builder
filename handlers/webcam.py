from aiogram import Router
from aiogram.types import Message, FSInputFile
import cv2, tempfile, os

router = Router()

@router.message(lambda m: m.text == "📷 Вебкамера")
async def webcam_photo(message: Message):
    await message.answer("📷 Делаю фото...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await message.answer("❌ Вебкамера не найдена")
        return
    ret, frame = cap.read()
    cap.release()
    if not ret:
        await message.answer("❌ Не удалось сделать фото")
        return
    path = tempfile.mktemp(suffix=".jpg")
    cv2.imwrite(path, frame)
    await message.answer_photo(FSInputFile(path))
    os.remove(path)
