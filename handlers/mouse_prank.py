from aiogram import Router
from aiogram.types import Message
import asyncio, pyautogui, random

router = Router()
prank_state = {"active": False}

@router.message(lambda m: m.text == "🔀 Бесить мышь")
async def start_mouse_prank(message: Message):
    if prank_state["active"]:
        await message.answer("⚠️ Уже активно. /stopmouse — остановить")
        return
    prank_state["active"] = True
    await message.answer("😈 Мышь начала жить своей жизнью!\n/stopmouse — остановить")

    async def prank_loop():
        while prank_state["active"]:
            x = random.randint(0, pyautogui.size().width)
            y = random.randint(0, pyautogui.size().height)
            pyautogui.moveTo(x, y, duration=0.3)
            await asyncio.sleep(random.uniform(0.5, 2.0))
        prank_state["active"] = False

    asyncio.create_task(prank_loop())

@router.message(lambda m: m.text == "/stopmouse")
async def stop_mouse_prank(message: Message):
    if not prank_state["active"]:
        await message.answer("❌ Не активно")
        return
    prank_state["active"] = False
    await message.answer("✅ Мышь успокоилась")
