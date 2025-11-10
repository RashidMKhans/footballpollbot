#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot для автоматической отправки опросов каждую среду в 11:00 (UTC+5)
PRODUCTION VERSION - использует webhook для бесплатного хостинга на Render
"""

import os
import logging
import asyncio
from datetime import time
from zoneinfo import ZoneInfo
from flask import Flask, request

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 10000))
TIMEZONE = ZoneInfo('Asia/Almaty')  # UTC+5

# Flask приложение
app = Flask(__name__)

# Глобальная переменная для Application
bot_application = None


async def send_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция для отправки опроса в группу.
    Вызывается автоматически по расписанию.
    """
    try:
        question = "🏃‍♂️Жұма 20:30 футбол НИШ"
        options = ["✅ Келемін буйыртса", "❌ Келе алмаймын"]

        # Отправка опроса
        await context.bot.send_poll(
            chat_id=CHAT_ID,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False,
        )

        # Отправка списка игроков
        player_list = """Жұма 20:30 футбол НИШ
        
FC
1.
2.
3.
4.
5.

FC
6.
7.
8.
9.
10.

FC
11.
12.
13.
14.
15."""

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=player_list
        )

        logger.info(f"Опрос и список игроков отправлены в группу {CHAT_ID}")

    except Exception as e:
        logger.error(f"Ошибка при отправке опроса: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🐅 Сәлем, Алтел Digital-дың жолбарыстары мен футболдағы қасқырлар! \n\n"
        "Мен — осы топтағы апталық жиналыстарды реттейтін сауалнама-ботпын.\n\n"
        "Әр сәрсенбі күні сағат 11:00-де (Алматы уақытымен) мен осы чатқа "
        "«Келем» немесе «Келмеймін» деген дауыс беру сауалнамасын жіберемін.\n\n"
    )


async def test_poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для тестовой отправки опроса"""
    try:
        question = "🏃‍♂️Жұма 20:30 футбол НИШ"
        options = ["✅ Келемін буйыртса", "❌ Келе алмаймын"]

        # Отправка опроса
        await update.message.reply_poll(
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False,
        )

        # Отправка списка игроков
        player_list = """Жұма 20:30 футбол НИШ
        
FC
1.
2.
3.
4.
5.

FC
6.
7.
8.
9.
10.

FC
11.
12.
13.
14.
15."""

        await update.message.reply_text(player_list)

        logger.info(f"Тестовый опрос и список игроков отправлены пользователем {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при отправке тестового опроса: {e}")
        await update.message.reply_text(f"Ошибка: {e}")


async def get_chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для получения ID текущего чата"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title if chat_type in ['group', 'supergroup'] else 'Личный чат'

    await update.message.reply_text(
        f"📋 Информация о чате:\n\n"
        f"ID чата: `{chat_id}`\n"
        f"Тип: {chat_type}\n"
        f"Название: {chat_title}\n\n"
        f"Используй этот ID в переменной CHAT_ID",
        parse_mode='Markdown'
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для остановки бота"""
    await update.message.reply_text(
        "⚠️ Команда /stop недоступна на production сервере.\n"
        "Для остановки бота используйте панель управления хостингом."
    )


async def post_init(application: Application) -> None:
    """
    Инициализация после запуска бота.
    """
    # Устанавливаем команды бота
    commands = [
        BotCommand("start_dop_tep", "Бот туралы ақпарат"),
        BotCommand("dop_tep_poll", "қасқырлар сауалнамасын жасау"),
        BotCommand("get_chat_id", "Получить ID чата"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Команды бота установлены")

    # Добавляем задачу: каждую среду в 11:00
    job_queue = application.job_queue
    job_queue.run_daily(
        send_poll,
        time=time(hour=11, minute=0, second=0, tzinfo=TIMEZONE),
        days=(2,),  # среда
        name='weekly_poll'
    )

    logger.info("✅ Расписание настроено: опросы будут отправляться каждую среду в 11:00 (UTC+5)")


# Flask routes
@app.route('/')
def index():
    """Root endpoint для проверки работоспособности"""
    return "🏃‍♂️ DopTep Poll Bot is running! ⚽", 200


@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200


@app.route('/telegram', methods=['POST'])
def webhook():
    """Webhook endpoint для Telegram"""
    global bot_application
    try:
        if bot_application:
            update = Update.de_json(request.get_json(force=True), bot_application.bot)
            asyncio.run(bot_application.process_update(update))
        return "ok", 200
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        return "error", 500


async def init_bot():
    """Инициализация бота"""
    global bot_application

    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен!")
        return

    if not CHAT_ID:
        logger.warning("⚠️ CHAT_ID не установлен")

    if not WEBHOOK_URL:
        logger.warning("⚠️ WEBHOOK_URL не установлен")

    # Создание приложения
    builder = Application.builder()
    builder.token(BOT_TOKEN)
    builder.post_init(post_init)
    bot_application = builder.build()

    # Регистрация обработчиков
    bot_application.add_handler(CommandHandler("start_dop_tep", start_command))
    bot_application.add_handler(CommandHandler("dop_tep_poll", test_poll_command))
    bot_application.add_handler(CommandHandler("get_chat_id", get_chat_id_command))
    bot_application.add_handler(CommandHandler("stop", stop_command))

    # Инициализация и запуск
    await bot_application.initialize()
    await bot_application.start()

    # Установка webhook
    webhook_url = f"{WEBHOOK_URL}/telegram"
    await bot_application.bot.set_webhook(url=webhook_url, drop_pending_updates=True)

    logger.info("🚀 Бот инициализирован и webhook установлен!")
    logger.info(f"🌐 Webhook URL: {webhook_url}")
    logger.info(f"🏥 Health check: {WEBHOOK_URL}/health")
    logger.info(f"🏥 Root endpoint: {WEBHOOK_URL}/")


def main() -> None:
    """Главная функция запуска бота"""

    # Инициализируем бота асинхронно
    asyncio.run(init_bot())

    # Запускаем Flask сервер
    logger.info(f"🌐 Запуск веб-сервера на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    main()
