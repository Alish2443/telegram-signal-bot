# Telegram Signal Bot

Бот для отправки VIP сигналов для игры Mines в 1win.

## 🚀 Деплой на Render (БЕСПЛАТНО - 24/7 работа)

### Шаг 1: Создайте аккаунт на Render
1. Перейдите на https://render.com/
2. Зарегистрируйтесь через GitHub (бесплатно)
3. Подтвердите email

### Шаг 2: Создайте новый Web Service
1. Нажмите "New +"
2. Выберите "Web Service"
3. Подключите ваш GitHub репозиторий `telegram-signal-bot`

### Шаг 3: Настройте сервис
- **Name**: `telegram-signal-bot`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python telegram_signal_bot.py`
- **Plan**: `Free` (бесплатный план)

### Шаг 4: Настройте переменные окружения
В разделе "Environment Variables" добавьте:
```
BOT_TOKEN=8351426493:AAEL5tOkQCMGP4aeEyzRqieuspIKR1kgRfA
PARTNER_LINK=https://1wbtqu.life/casino/list?open=register&p=ufc1
PROMO_CODE=AVIATWIN
```

### Шаг 5: Запустите деплой
1. Нажмите "Create Web Service"
2. Render автоматически развернет ваш бот
3. Дождитесь статуса "Live"

### Шаг 6: Проверьте работу
1. Перейдите в раздел "Logs"
2. Убедитесь, что нет ошибок
3. Протестируйте бота в Telegram

## 🐳 Альтернативный деплой с Docker

Если нужен Docker:
1. В Render выберите "Docker" как Environment
2. Build Command: оставьте пустым
3. Start Command: `python telegram_signal_bot.py`

## 🔧 Локальная разработка

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск бота
```bash
python telegram_signal_bot.py
```

## 📁 Структура проекта

- `telegram_signal_bot.py` - основной файл бота
- `requirements.txt` - зависимости Python
- `Procfile` - конфигурация для Heroku/Railway
- `railway.json` - конфигурация Railway
- `nixpacks.toml` - конфигурация сборки
- `Dockerfile` - конфигурация Docker
- `render.yaml` - конфигурация Render

## 🎯 Функции бота

- ✅ Регистрация пользователей
- ✅ Проверка ID через веб-скрапинг
- ✅ Генерация VIP сигналов
- ✅ Автообновление сигналов
- ✅ Статистика пользователей
- ✅ Проверка баланса
- ✅ Настройки автообновления

## 🔗 Ссылки

- [Render Dashboard](https://dashboard.render.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [1win Casino](https://1wbtqu.life/casino/list?open=register&p=ufc1) 