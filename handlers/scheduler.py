from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio, subprocess
from datetime import datetime, timedelta

router = Router()
tasks = {}

class SchedState(StatesGroup):
    waiting_time = State()
    waiting_cmd = State()

@router.message(lambda m: m.text == "⏰ Планировщик")
async def sched_menu(message: Message):
    text = "⏰ <b>Планировщик задач</b>\n\n"
    if tasks:
        for tid, t in tasks.items():
            text += f"<code>{tid}</code> | {t['time']} | {t['cmd']}\n"
        text += "\n/deltask [id] — удалить задачу"
    else:
        text += "Задач нет."
    text += "\n\n/addtask — добавить задачу"
    await message.answer(text)

@router.message(lambda m: m.text == "/addtask")
async def add_task_time(message: Message, state: FSMContext):
    await message.answer("Введи время запуска (формат HH:MM, например 14:30):")
    await state.set_state(SchedState.waiting_time)

@router.message(SchedState.waiting_time)
async def add_task_cmd(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), "%H:%M")
    except ValueError:
        await message.answer("❌ Неверный формат. Пример: 14:30")
        return
    await state.update_data(time=message.text.strip())
    await message.answer("Введи команду для запуска:")
    await state.set_state(SchedState.waiting_cmd)

@router.message(SchedState.waiting_cmd)
async def save_task(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    await state.clear()
    tid = str(len(tasks) + 1)
    tasks[tid] = {"time": data["time"], "cmd": message.text}
    await message.answer(f"✅ Задача #{tid} добавлена: {data['time']} → {message.text}")
    asyncio.create_task(run_at(tid, data["time"], message.text, message.chat.id, bot))

async def run_at(tid, time_str, cmd, chat_id, bot):
    now = datetime.now()
    target = datetime.strptime(time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    if target <= now:
        target += timedelta(days=1)
    wait_sec = (target - now).total_seconds()
    await asyncio.sleep(wait_sec)
    if tid in tasks:
        subprocess.Popen(cmd, shell=True)
        await bot.send_message(chat_id, f"⏰ Задача #{tid} выполнена: {cmd}")
        tasks.pop(tid, None)

@router.message(F.text.startswith("/deltask"))
async def del_task(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Укажи ID: /deltask 1")
        return
    tid = parts[1]
    if tid in tasks:
        tasks.pop(tid)
        await message.answer(f"✅ Задача #{tid} удалена")
    else:
        await message.answer("❌ Задача не найдена")
