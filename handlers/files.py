from aiogram import Router, F
from aiogram.types import Message, FSInputFile, Document
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

router = Router()

class FileState(StatesGroup):
    waiting_path = State()
    waiting_upload = State()

@router.message(lambda m: m.text == "📁 Файлы")
async def files_menu(message: Message):
    await message.answer(
        "📁 <b>Файловый менеджер</b>\n\n"
        "Команды:\n"
        "/ls [путь] — список файлов\n"
        "/download [путь] — скачать файл\n"
        "/upload — загрузить файл на ПК",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("/ls"))
async def list_files(message: Message):
    parts = message.text.split(maxsplit=1)
    path = parts[1] if len(parts) > 1 else os.path.expanduser("~")
    try:
        entries = os.listdir(path)
        if not entries:
            await message.answer("📂 Папка пустая")
            return
        text = f"📂 <b>{path}</b>\n\n"
        for e in entries[:50]:
            full = os.path.join(path, e)
            icon = "📁" if os.path.isdir(full) else "📄"
            text += f"{icon} {e}\n"
        if len(entries) > 50:
            text += f"\n...и ещё {len(entries) - 50} файлов"
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(F.text.startswith("/download"))
async def download_file(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи путь: /download C:\\Users\\...\\file.txt")
        return
    path = parts[1].strip()
    try:
        await message.answer_document(FSInputFile(path))
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(lambda m: m.text == "/upload")
async def ask_upload(message: Message, state: FSMContext):
    await message.answer("Отправь файл, и он сохранится в папку Загрузки:")
    await state.set_state(FileState.waiting_upload)

@router.message(FileState.waiting_upload, F.document)
async def save_upload(message: Message, state: FSMContext, bot):
    await state.clear()
    file = message.document
    downloads = os.path.join(os.path.expanduser("~"), "Downloads", file.file_name)
    file_info = await bot.get_file(file.file_id)
    await bot.download_file(file_info.file_path, downloads)
    await message.answer(f"✅ Файл сохранён: {downloads}")
