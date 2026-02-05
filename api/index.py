import os
import json
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder

# Импортируем функцию регистрации из вашего файла bot.py
from bot import register_handlers

# Инициализируем FastAPI
app = FastAPI()

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Создаем приложение бота глобально, чтобы не пересоздавать при каждом запросе (по возможности)
bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app = register_handlers(bot_app)

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """
    Эта функция получает обновления от Telegram
    и передает их в python-telegram-bot
    """
    # 1. Получаем JSON из запроса
    data = await request.json()
    
    # 2. Преобразуем JSON в объект Update
    update = Update.de_json(data, bot_app.bot)
    
    # 3. Инициализируем приложение бота (если нужно) и обрабатываем обновление
    async with bot_app:
        # Важно: process_update обрабатывает одно сообщение
        await bot_app.process_update(update)
    
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "Bot is running on Vercel!"}
