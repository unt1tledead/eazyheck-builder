from aiogram import Router
from aiogram.types import Message
import psutil, platform

router = Router()

@router.message(lambda m: m.text == "💻 Система")
async def system_info(message: Message):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    text = (
        f"💻 <b>Система</b>\n\n"
        f"🖥 ОС: {platform.system()} {platform.release()}\n"
        f"⚙️ CPU: {cpu}%\n"
        f"🧠 RAM: {ram.used // 1024**2} МБ / {ram.total // 1024**2} МБ ({ram.percent}%)\n"
        f"💾 Диск: {disk.used // 1024**3} ГБ / {disk.total // 1024**3} ГБ ({disk.percent}%)"
    )
    await message.answer(text, parse_mode="HTML")
