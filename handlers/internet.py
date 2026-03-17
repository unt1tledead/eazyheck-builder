from aiogram import Router
from aiogram.types import Message
import subprocess, asyncio, time

router = Router()

@router.message(lambda m: m.text == "📡 Интернет")
async def internet_check(message: Message):
    await message.answer("📡 Проверяю соединение...")
    
    ping_ms = None
    try:
        start = time.time()
        result = subprocess.run(
            ["ping", "-n", "4", "8.8.8.8"],
            capture_output=True, timeout=10
        )
        output = result.stdout.decode("cp866", errors="ignore") + result.stdout.decode("utf-8", errors="ignore")
        elapsed = (time.time() - start) * 1000
        for line in output.split("\n"):
            if "Среднее" in line or "Average" in line or "средн" in line.lower():
                for part in line.split("="):
                    part = part.strip().replace("мс", "").replace("ms", "").strip()
                    if part.isdigit():
                        ping_ms = int(part)
                        break
        if ping_ms is None:
            ping_ms = int(elapsed / 4)
    except Exception:
        ping_ms = None

    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "$r=(Invoke-WebRequest -Uri 'https://speed.cloudflare.com/__down?bytes=5000000' -UseBasicParsing); $r.RawContentLength"],
            capture_output=True, text=True, timeout=20
        )
        size = int(result.stdout.strip())
        speed_mbps = round((size * 8) / (1024 * 1024 * 5), 1)
    except Exception:
        speed_mbps = None

    emoji_ping = "🟢" if ping_ms and ping_ms < 50 else "🟡" if ping_ms and ping_ms < 150 else "🔴"
    ping_text = f"{emoji_ping} Пинг: {ping_ms} мс" if ping_ms else "❌ Пинг: нет ответа"
    speed_text = f"⚡ Скорость: ~{speed_mbps} Мбит/с" if speed_mbps else "❌ Скорость: не удалось измерить"

    await message.answer(f"📡 <b>Интернет</b>\n\n{ping_text}\n{speed_text}")
