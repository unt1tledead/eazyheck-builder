from aiogram import Router
from aiogram.types import Message
import subprocess, sys

router = Router()

@router.message(lambda m: m.text == "/stealth")
async def stealth_mode(message: Message):
    await message.answer("🕵️ Переключаюсь в скрытый режим...")
    if sys.platform == "win32":
        script = '''
$code = @"
using System;
using System.Runtime.InteropServices;
public class Win {
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@
Add-Type -TypeDefinition $code
$hwnd = [Win]::GetConsoleWindow()
[Win]::ShowWindow($hwnd, 0)
'''
        subprocess.Popen(["powershell", "-Command", script])
        await message.answer("🕵️ Консоль скрыта. /showwindow — вернуть обратно")
    else:
        await message.answer("❌ Скрытый режим доступен только на Windows")

@router.message(lambda m: m.text == "/showwindow")
async def show_window(message: Message):
    if sys.platform == "win32":
        script = '''
$code = @"
using System;
using System.Runtime.InteropServices;
public class Win {
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@
Add-Type -TypeDefinition $code
$hwnd = [Win]::GetConsoleWindow()
[Win]::ShowWindow($hwnd, 5)
'''
        subprocess.Popen(["powershell", "-Command", script])
        await message.answer("🖥 Окно показано")
    else:
        await message.answer("❌ Только Windows")
