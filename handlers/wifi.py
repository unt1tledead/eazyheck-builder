from aiogram import Router
from aiogram.types import Message
import subprocess, sys

router = Router()

@router.message(lambda m: m.text == "🔌 Wi-Fi сети")
async def wifi_list(message: Message):
    await message.answer("🔌 Сканирую сети...")
    try:
        if sys.platform == "win32":
            for enc in ("utf-8", "cp1251", "cp866"):
                try:
                    result = subprocess.run(
                        ["netsh", "wlan", "show", "networks", "mode=bssid"],
                        capture_output=True, timeout=10
                    )
                    output = result.stdout.decode(enc, errors="ignore")
                    break
                except Exception:
                    continue
            lines = output.split("\n")
            networks = []
            name, signal = None, None
            for line in lines:
                if "SSID" in line and "BSSID" not in line and ":" in line:
                    name = line.split(":", 1)[1].strip()
                if ("Сигнал" in line or "Signal" in line) and ":" in line:
                    signal = line.split(":", 1)[1].strip()
                if name and signal:
                    networks.append((name, signal))
                    name, signal = None, None
        else:
            result = subprocess.run(
                ["nmcli", "-f", "SSID,SIGNAL", "dev", "wifi"],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().split("\n")[1:]
            networks = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    networks.append((" ".join(parts[:-1]), parts[-1] + "%"))

        if not networks:
            await message.answer("❌ Сети не найдены")
            return

        text = "🔌 <b>Wi-Fi сети:</b>\n\n"
        for name, signal in networks[:20]:
            text += f"📶 <b>{name}</b> — {signal}\n"
        await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
