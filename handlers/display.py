from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import subprocess

router = Router()

class DisplayState(StatesGroup):
    waiting_brightness = State()

RESOLUTIONS = [
    ("1920x1080", 1920, 1080),
    ("2560x1440", 2560, 1440),
    ("1280x720", 1280, 720),
    ("1366x768", 1366, 768),
    ("1600x900", 1600, 900),
    ("3840x2160", 3840, 2160),
]

display_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🖥 Разрешение", callback_data="disp_res"),
     InlineKeyboardButton(text="☀️ Яркость", callback_data="disp_bright")],
    [InlineKeyboardButton(text="🌙 Тёмная тема", callback_data="disp_dark", style="primary"),
     InlineKeyboardButton(text="☀️ Светлая тема", callback_data="disp_light", style="primary")],
])

res_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=r[0], callback_data=f"res_{r[1]}_{r[2]}")]
    for r in RESOLUTIONS
] + [[InlineKeyboardButton(text="◀️ Назад", callback_data="disp_back")]])

@router.message(lambda m: m.text == "📺 Дисплей")
async def display_menu(message: Message):
    await message.answer("📺 <b>Управление дисплеем</b>", reply_markup=display_kb)

@router.callback_query(lambda c: c.data.startswith("disp_"))
async def display_action(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    if action == "disp_res":
        await callback.message.edit_text("🖥 Выбери разрешение:", reply_markup=res_kb)
        await callback.answer()
    elif action == "disp_bright":
        await callback.message.answer("Введи яркость от 0 до 100:")
        await state.set_state(DisplayState.waiting_brightness)
        await callback.answer()
    elif action == "disp_dark":
        subprocess.Popen(["powershell", "-Command",
            "Set-ItemProperty -Path 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name AppsUseLightTheme -Value 0; "
            "Set-ItemProperty -Path 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name SystemUsesLightTheme -Value 0"])
        await callback.answer("🌙 Тёмная тема включена")
    elif action == "disp_light":
        subprocess.Popen(["powershell", "-Command",
            "Set-ItemProperty -Path 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name AppsUseLightTheme -Value 1; "
            "Set-ItemProperty -Path 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name SystemUsesLightTheme -Value 1"])
        await callback.answer("☀️ Светлая тема включена")
    elif action == "disp_back":
        await callback.message.edit_text("📺 <b>Управление дисплеем</b>", reply_markup=display_kb)
        await callback.answer()

@router.callback_query(lambda c: c.data.startswith("res_"))
async def set_resolution(callback: CallbackQuery):
    parts = callback.data.split("_")
    w, h = int(parts[1]), int(parts[2])
    script = f"""
Add-Type @"
using System.Runtime.InteropServices;
public class Display {{
    [DllImport("user32.dll")] public static extern int ChangeDisplaySettings(ref DEVMODE dm, int flags);
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Ansi)]
    public struct DEVMODE {{
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmDeviceName;
        public short dmSpecVersion, dmDriverVersion, dmSize, dmDriverExtra;
        public int dmFields, dmPositionX, dmPositionY, dmDisplayOrientation, dmDisplayFixedOutput;
        public short dmColor, dmDuplex, dmYResolution, dmTTOption, dmCollate;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmFormName;
        public short dmLogPixels; public int dmBitsPerPel, dmPelsWidth, dmPelsHeight, dmDisplayFlags, dmDisplayFrequency;
    }}
}}
"@
$dm = New-Object Display+DEVMODE
$dm.dmSize = [System.Runtime.InteropServices.Marshal]::SizeOf($dm)
$dm.dmPelsWidth = {w}; $dm.dmPelsHeight = {h}; $dm.dmFields = 0x180000
[Display]::ChangeDisplaySettings([ref]$dm, 0)
"""
    result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        await callback.answer(f"✅ {w}x{h}")
        await callback.message.edit_text(f"✅ Разрешение изменено на {w}x{h}", reply_markup=display_kb)
    else:
        await callback.answer("❌ Ошибка")

@router.message(DisplayState.waiting_brightness)
async def set_brightness(message: Message, state: FSMContext):
    await state.clear()
    try:
        val = max(0, min(100, int(message.text.strip())))
        subprocess.Popen(["powershell", "-Command",
            f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{val})"])
        await message.answer(f"☀️ Яркость: {val}%")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
