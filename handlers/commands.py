from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import subprocess

router = Router()

class CmdState(StatesGroup):
    waiting = State()

@router.message(lambda m: m.text == "⚙️ Команда")
async def ask_command(message: Message, state: FSMContext):
    await message.answer("Введи команду для выполнения:")
    await state.set_state(CmdState.waiting)

@router.message(CmdState.waiting)
async def run_command(message: Message, state: FSMContext):
    await state.clear()
    try:
        result = subprocess.run(
            message.text, shell=True, capture_output=True, text=True, timeout=15
        )
        output = result.stdout or result.stderr or "(нет вывода)"
        if len(output) > 4000:
            output = output[:4000] + "\n...(обрезано)"
        await message.answer(f"<pre>{output}</pre>", parse_mode="HTML")
    except subprocess.TimeoutExpired:
        await message.answer("⏱ Превышено время ожидания (15 сек)")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
