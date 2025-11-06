#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot для автоматической отправки опросов каждую среду в 11:00 (UTC+5)
PRODUCTION VERSION - использует переменные окружения
"""

import os
import logging
from datetime import time
from zoneinfo import ZoneInfo

from telegram import Update, Bot, BotCommand
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

# Конфигурация из переменных окружения (для деплоя)
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # ID группы, куда отправлять опрос
TIMEZONE = ZoneInfo('Asia/Almaty')  # UTC+5 (Алматы/Астана)


async def send_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция для отправки опроса в группу.
    Вызывается автоматически по расписанию.
    """
    try:
        question = "🏃‍♂️Жұма 20:30 футбол ниш"
        options = ["✅ Келем буйыртса", "❌ Келе алмайм"]

        # Отправка неанонимного опроса
        await context.bot.send_poll(
            chat_id=CHAT_ID,
            question=question,
            options=options,
            is_anonymous=False,  # Неанонимный опрос
            allows_multiple_answers=False,  # Только один ответ
        )

        logger.info(f"Опрос успешно отправлен в группу {CHAT_ID}")

    except Exception as e:
        logger.error(f"Ошибка при отправке опроса: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        "👋 Привет! Я бот для автоматических опросов.\n\n"
        "Каждую среду в 11:00 (по времени Алматы) я буду отправлять "
        "опрос в заданную группу.\n\n"
        "Убедись, что:\n"
        "1. Я добавлен в группу\n"
        "2. У меня есть права администратора\n"
        "3. Настроен CHAT_ID в переменных окружения"
    )


async def test_poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для тестовой отправки опроса (только для админа)"""
    try:
        question = "🏃‍♂️Жұма 20:30 футбол ниш"
        options = ["✅ Келем буйыртса", "❌ Келе алмайм"]

        await update.message.reply_poll(
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False,
        )

        logger.info(f"Тестовый опрос отправлен пользователем {update.effective_user.id}")

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
    await update.message.reply_text("🛑 Останавливаю бот...")
    logger.info(f"Бот остановлен пользователем {update.effective_user.id}")

    # Останавливаем приложение
    application = context.application
    await application.stop()
    await application.shutdown()


async def post_init(application: Application) -> None:
    """
    Инициализация после запуска бота.
    Настраивает расписание для отправки опросов.
    """
    # Устанавливаем команды бота для отображения в меню Telegram
    commands = [
        BotCommand("start_dop_tep", "Информация о боте"),
        BotCommand("dop_tep_poll", "Отправить опрос"),
        BotCommand("get_chat_id", "Получить ID текущего чата"),
        BotCommand("stop", "Остановить бот"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Команды бота установлены")

    job_queue = application.job_queue

    # Добавляем задачу: каждую среду в 11:00 по времени Алматы (UTC+5)
    job_queue.run_daily(
        send_poll,
        time=time(hour=11, minute=0, second=0, tzinfo=TIMEZONE),
        days=(2,),  # 2 = среда (0=понедельник, 1=вторник, 2=среда, ...)
        name='weekly_poll'
    )

    logger.info("✅ Расписание настроено: опросы будут отправляться каждую среду в 11:00 (UTC+5)")


def main() -> None:
    """Главная функция запуска бота"""

    # Проверка наличия токена
    if not BOT_TOKEN:
        logger.error("❌ Ошибка: BOT_TOKEN не установлен в переменных окружения!")
        return

    if not CHAT_ID:
        logger.warning("⚠️ Предупреждение: CHAT_ID не установлен. Используй команду /get_chat_id в группе для получения ID")

    # Создание приложения
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start_dop_tep", start_command))
    application.add_handler(CommandHandler("dop_tep_poll", test_poll_command))
    application.add_handler(CommandHandler("get_chat_id", get_chat_id_command))
    application.add_handler(CommandHandler("stop", stop_command))

    # Запуск бота
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
