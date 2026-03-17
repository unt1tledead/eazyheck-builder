from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import subprocess, sys

router = Router()

class NotifState(StatesGroup):
    waiting = State()

@router.message(lambda m: m.text == "🔔 Уведомление")
async def ask_notif(message: Message, state: FSMContext):
    await message.answer("Введи текст уведомления:")
    await state.set_state(NotifState.waiting)

@router.message(NotifState.waiting)
async def send_notif(message: Message, state: FSMContext):
    await state.clear()
    text = message.text
    
    try:
        if sys.platform == "win32":
            script = f'''
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.ShowBalloonTip(5000, "EazyHeck", "{text}", [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 6
$notify.Dispose()
'''
            subprocess.Popen(["powershell", "-Command", script])
        elif sys.platform == "darwin":
            subprocess.Popen(["osascript", "-e", f'display notification "{text}" with title "EazyHeck"'])
        else:
            subprocess.Popen(["notify-send", "EazyHeck", text])
        
        await message.answer(f"✅ Уведомление отправлено: {text}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
