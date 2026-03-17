from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import psutil

router = Router()

class KillState(StatesGroup):
    waiting_pid = State()

@router.message(lambda m: m.text == "🔧 Процессы")
async def list_processes(message: Message):
    procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']),
                   key=lambda p: p.info['cpu_percent'] or 0, reverse=True)
    text = "🔧 <b>Топ процессов по CPU</b>\n\n"
    for p in procs[:20]:
        mem = (p.info['memory_info'].rss // 1024**2) if p.info['memory_info'] else 0
        text += f"<code>{p.info['pid']}</code> | {p.info['name'][:25]} | CPU: {p.info['cpu_percent']}% | RAM: {mem}МБ\n"
    text += "\nЧтобы завершить: /kill [pid]"
    await message.answer(text, parse_mode="HTML")

@router.message(F.text.startswith("/kill"))
async def kill_process(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Укажи PID: /kill 1234")
        return
    try:
        pid = int(parts[1])
        p = psutil.Process(pid)
        name = p.name()
        p.kill()
        await message.answer(f"✅ Процесс {name} (PID {pid}) завершён")
    except psutil.NoSuchProcess:
        await message.answer("❌ Процесс не найден")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
