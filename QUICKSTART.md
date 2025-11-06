# Быстрый старт за 5 минут

## 1. Создай бота

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot` и следуй инструкциям
3. Скопируй токен (вида: `123456:ABC...`)
4. Отправь `/mybots` → выбери бота → **Bot Settings** → **Group Privacy** → **Turn off**

## 2. Настрой группу

1. Добавь бота в свою группу
2. Сделай его **администратором** (права на отправку сообщений)
3. Отправь `/get_chat_id` в группе
4. Скопируй ID группы (например: `-1001234567890`)

## 3. Задеплой на Render.com

1. Загрузи код на GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git push
```

2. Перейди на [render.com](https://render.com) → зарегистрируйся через GitHub

3. **New +** → **Background Worker**

4. Выбери свой репозиторий

5. Заполни:
   - **Name:** `doptep-poll-bot`
   - **Start Command:** `python bot.py`
   - **Plan:** Free

6. Добавь **Environment Variables:**
   - `BOT_TOKEN` = твой токен
   - `CHAT_ID` = твой ID группы

7. Нажми **Create Background Worker**

## 4. Проверь

- Команда `/test_poll` — немедленная проверка
- Каждую среду в 11:00 (UTC+5) бот сам отправит опрос

## Готово!

Подробные инструкции: [README.md](README.md)
