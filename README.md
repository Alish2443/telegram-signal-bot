# Telegram Signal Bot

Бот для отправки VIP сигналов для игры Mines в 1win.

## 🚀 Деплой на Railway (24/7 работа)

### Шаг 1: Создайте аккаунт на Railway
1. Перейдите на https://railway.app/
2. Зарегистрируйтесь через GitHub
3. Подключите ваш GitHub аккаунт

### Шаг 2: Разверните проект
1. Нажмите "New Project"
2. Выберите "Deploy from GitHub repo"
3. Найдите ваш репозиторий `telegram-signal-bot`
4. Нажмите "Deploy Now"

### Шаг 3: Настройте переменные окружения
В Railway Dashboard перейдите в раздел "Variables" и добавьте:

```
BOT_TOKEN=8351426493:AAEL5tOkQCMGP4aeEyzRqieuspIKR1kgRfA
PARTNER_LINK=https://1wbtqu.life/casino/list?open=register&p=ufc1
PROMO_CODE=AVIATWIN
```

### Шаг 4: Проверьте деплой
1. Перейдите в раздел "Deployments"
2. Убедитесь, что статус "Deployed"
3. Проверьте логи на наличие ошибок

### 🔧 Исправление ошибок деплоя

Если возникает ошибка с Nixpacks:
1. В Railway Dashboard перейдите в "Settings"
2. В разделе "Build & Deploy" выберите "Dockerfile" вместо "Nixpacks"
3. Перезапустите деплой

## 🐳 Альтернативный деплой с Docker

Если Railway не работает, используйте Docker:

1. **Создайте аккаунт на Render**: https://render.com/
2. **Создайте новый Web Service**:
   - Подключите GitHub репозиторий
   - Выберите "Docker" как Environment
   - Build Command: оставьте пустым
   - Start Command: `python telegram_signal_bot.py`

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

- [Railway Dashboard](https://railway.app/dashboard)
- [Render Dashboard](https://dashboard.render.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [1win Casino](https://1wbtqu.life/casino/list?open=register&p=ufc1) 