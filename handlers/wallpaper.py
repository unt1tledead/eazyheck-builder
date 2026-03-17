from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import ctypes, os, tempfile

router = Router()

class WallpaperState(StatesGroup):
    waiting_photo = State()

@router.message(lambda m: m.text == "🎨 Обои")
async def ask_wallpaper(message: Message, state: FSMContext):
    await message.answer("🎨 Отправь фото — поставлю как обои рабочего стола:")
    await state.set_state(WallpaperState.waiting_photo)

@router.message(WallpaperState.waiting_photo, F.photo)
async def set_wallpaper(message: Message, state: FSMContext, bot):
    await state.clear()
    await message.answer("⏳ Устанавливаю обои...")
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    path = os.path.join(tempfile.gettempdir(), "eazyheck_wallpaper.jpg")
    await bot.download_file(file_info.file_path, path)
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        await message.answer("✅ Обои установлены!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
