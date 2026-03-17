from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio, threading, sys

router = Router()

chat_state = {
    "active": False,
    "bot": None,
    "chat_id": None,
}

MENU_BUTTONS = {
    "📊 График", "🌐 Открыть URL", "📦 Программы", "📡 Интернет",
    "⚙️ Команда", "📸 Скриншот", "⏰ Планировщик", "📷 Вебкамера",
    "📺 Дисплей", "🔌 Wi-Fi сети", "🔴 Запись экрана", "🔊 Громкость",
    "🔔 Уведомление", "🎵 Медиа", "📋 Буфер", "🖱 Мышь/Клава",
    "💻 Система", "🔑 Кейлоггер", "📁 Файлы", "🔐 Автозапуск",
    "💬 Чат с ПК", "🔧 Процессы", "⏻ Питание",
}

chat_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Закрыть чат", callback_data="chat_close", style="danger")]
])

def open_chat_window(text: str, bot, chat_id, loop):
    if sys.platform != "win32":
        return
    import tkinter as tk

    def send_reply():
        reply = entry.get("1.0", "end-1c").strip()
        if reply:
            asyncio.run_coroutine_threadsafe(
                bot.send_message(chat_id, f"💻 <b>ПК:</b> {reply}"),
                loop
            )
        root.destroy()

    def on_close():
        root.destroy()

    root = tk.Tk()
    root.title("EazyHeck Chat")
    root.geometry("420x230")
    root.configure(bg="#1e1e1e")
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(root, text="📨 Новое сообщение:", bg="#1e1e1e", fg="#aaaaaa",
             font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(10, 2))
    tk.Label(root, text=text, bg="#2b2b2b", fg="white", font=("Segoe UI", 11),
             wraplength=390, justify="left", padx=8, pady=6).pack(fill="x", padx=10)

    tk.Label(root, text="✏️ Ответ:", bg="#1e1e1e", fg="#aaaaaa",
             font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(10, 2))
    entry = tk.Text(root, height=3, bg="#2b2b2b", fg="white", insertbackground="white",
                    font=("Segoe UI", 11), relief="flat", padx=6, pady=4)
    entry.pack(fill="x", padx=10)
    entry.focus()

    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(fill="x", padx=10, pady=8)
    tk.Button(btn_frame, text="📤 Отправить", command=send_reply,
              bg="#0088cc", fg="white", font=("Segoe UI", 10, "bold"),
              relief="flat", padx=12, pady=4).pack(side="left")
    tk.Button(btn_frame, text="Закрыть", command=on_close,
              bg="#333", fg="#aaa", font=("Segoe UI", 10),
              relief="flat", padx=12, pady=4).pack(side="right")

    root.mainloop()

def is_chat_message(m: Message) -> bool:
    return (
        chat_state["active"]
        and bool(m.text)
        and not m.text.startswith("/")
        and m.text not in MENU_BUTTONS
    )

@router.message(lambda m: m.text == "💬 Чат с ПК")
async def start_chat(message: Message, bot):
    if chat_state["active"]:
        await message.answer("💬 Чат уже активен. Пиши сообщения!\n/stopchat — закрыть")
        return
    chat_state.update({"active": True, "bot": bot, "chat_id": message.chat.id})
    await message.answer(
        "💬 <b>Чат с ПК активен</b>\n\n"
        "Твои сообщения будут появляться в окне на ПК.\n"
        "Человек за компом может ответить — ответ придёт сюда.\n\n"
        "/stopchat — закрыть чат",
        reply_markup=chat_kb
    )

@router.message(lambda m: m.text == "/stopchat")
async def stop_chat(message: Message):
    if not chat_state["active"]:
        await message.answer("❌ Чат не активен")
        return
    chat_state["active"] = False
    await message.answer("💬 Чат закрыт")

@router.callback_query(lambda c: c.data == "chat_close")
async def close_chat_cb(callback: CallbackQuery):
    chat_state["active"] = False
    await callback.message.edit_text("💬 Чат закрыт")
    await callback.answer()

@router.message(is_chat_message)
async def forward_to_pc(message: Message, bot):
    loop = asyncio.get_event_loop()
    threading.Thread(
        target=open_chat_window,
        args=(message.text, bot, message.chat.id, loop),
        daemon=True
    ).start()
    await message.answer("✅ Сообщение отправлено на ПК")
