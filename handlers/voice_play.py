from aiogram import Router, F
from aiogram.types import Message
import os, tempfile, subprocess, sys

router = Router()

@router.message(F.voice)
async def play_voice(message: Message, bot):
    await message.answer("🔊 Воспроизвожу на ПК...")
    file_info = await bot.get_file(message.voice.file_id)
    ogg_path = os.path.join(tempfile.gettempdir(), "eazyheck_voice.ogg")
    await bot.download_file(file_info.file_path, ogg_path)
    try:
        if sys.platform == "win32":
            mp3_path = ogg_path.replace(".ogg", ".mp3")
            result = subprocess.run(
                ["powershell", "-Command",
                 f"$player = New-Object System.Media.SoundPlayer; "
                 f"Add-Type -AssemblyName presentationCore; "
                 f"$media = New-Object System.Windows.Media.MediaPlayer; "
                 f"$media.Open([uri]'{ogg_path}'); $media.Play(); Start-Sleep -Seconds 10; $media.Stop()"],
                capture_output=True, timeout=15
            )
        else:
            subprocess.Popen(["ffplay", "-nodisp", "-autoexit", ogg_path])
        await message.answer("✅ Воспроизводится!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
