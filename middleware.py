from aiogram import BaseMiddleware
from aiogram.types import Message
from config import ALLOWED_USER_ID

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if event.from_user.id != ALLOWED_USER_ID:
            await event.answer("⛔ Нет доступа.")
            return
        return await handler(event, data)
