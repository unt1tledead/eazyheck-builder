from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import cv2, numpy as np, pyautogui, threading, time, tempfile, os

router = Router()
recording = {"active": False, "thread": None, "path": None}

class RecordState(StatesGroup):
    recording = State()

def record_screen(path, stop_event):
    size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, 10.0, size)
    while not stop_event.is_set():
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)
        time.sleep(0.1)
    out.release()

@router.message(lambda m: m.text == "🔴 Запись экрана")
async def start_record(message: Message, state: FSMContext):
    if recording["active"]:
        await message.answer("⏹ Запись уже идёт. Отправь /stoprecord чтобы остановить.")
        return
    
    path = tempfile.mktemp(suffix=".mp4")
    stop_event = threading.Event()
    recording.update({"active": True, "path": path, "stop": stop_event})
    
    t = threading.Thread(target=record_screen, args=(path, stop_event), daemon=True)
    t.start()
    recording["thread"] = t
    
    await message.answer("🔴 Запись началась!\nОтправь /stoprecord чтобы остановить.")

@router.message(lambda m: m.text == "/stoprecord")
async def stop_record(message: Message):
    if not recording["active"]:
        await message.answer("❌ Запись не ведётся")
        return
    
    await message.answer("⏳ Останавливаю запись...")
    recording["stop"].set()
    recording["thread"].join(timeout=5)
    recording["active"] = False
    
    path = recording["path"]
    if os.path.exists(path) and os.path.getsize(path) > 0:
        await message.answer_video(FSInputFile(path), caption="🎥 Запись экрана")
        os.remove(path)
    else:
        await message.answer("❌ Файл не создался")
