# -*- coding: utf-8 -*-
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from aiohttp import web
import aiohttp

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ваши токены
TOKEN = os.environ.get("8391284559:AAHPWJWxtjM2AQTNJLDMGhTvgk-ZiM0U384")
SUNO_API_KEY = os.environ.get("796f8ced625a2d8904564b41ed4d560e")
PORT = int(os.environ.get('PORT', 10000))  # Render задает порт через переменную PORT

# Обработчики команд и сообщений (оставьте ваши функции start и handle_description без изменений)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "Привет! Я бот для генерации музыки с помощью Suno AI. 🎵\n\n"
        "Просто напиши мне описание песни, которую ты хочешь услышать, "
        "и я создам ее для тебя!\n\n"
        "Например, попробуй отправить: 'Веселая поп-песня о лете'"
    )
    await update.message.reply_text(welcome_text)

async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_prompt = update.message.text
    await update.message.reply_text("🎵 Принял твой запрос! Генерирую музыку... Это займет несколько минут.")
    # ... (ваш код генерации через Suno)

# Создаем приложение
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))

# Обработчик для вебхука от Telegram
async def telegram_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response()

# Запускаем сервер для Render
async def main():
    # Убеждаемся, что вебхук установлен на ваш URL от Render
    await application.bot.set_webhook(url=os.environ.get("RENDER_EXTERNAL_URL") + "/webhook")
    
    # Настраиваем aiohttp приложение
    app = web.Application()
    app.router.add_post("/webhook", telegram_webhook)
    
    # Запускаем сервер на правильном IP и порту
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
    await site.start()
    print(f"Сервер запущен на порту {PORT}")
    
    # Бесконечно ждем
    await asyncio.Future()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
