from fastapi import FastAPI, Request
from telegram import Update
# Импортируем функцию создания бота из твоего файла bot.py
# Используем get_application, так как в новом bot.py это главная функция
from bot import get_application

app = FastAPI()

# Глобальная переменная для приложения
ptb_app = None

@app.on_event("startup")
async def startup_event():
    """Инициализация бота при старте сервера"""
    global ptb_app
    if ptb_app is None:
        # get_application() сама создает и возвращает готовое приложение
        ptb_app = get_application()
        await ptb_app.initialize()
        await ptb_app.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Корректно останавливаем приложение PTB"""
    global ptb_app
    if ptb_app is not None:
        await ptb_app.stop()
        await ptb_app.shutdown()
        ptb_app = None

@app.post("/api/webhook")
async def webhook(request: Request):
    """Обработчик входящих сообщений от Telegram"""
    global ptb_app
    
    # На случай холодного старта, если startup не сработал
    if ptb_app is None:
        ptb_app = get_application()
        await ptb_app.initialize()
        await ptb_app.start()

    # Получаем данные и обрабатываем
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    
    await ptb_app.process_update(update)
    
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "Bot is running on Vercel!"}
