# 🚀 Развертывание Telegram-бота на Railway (24/7)

## 📋 Что нужно сделать:

### 1. **Создать аккаунт на Railway**
- Перейдите на https://railway.app/
- Зарегистрируйтесь через GitHub
- Подтвердите email

### 2. **Создать новый проект**
- Нажмите "New Project"
- Выберите "Deploy from GitHub repo"
- Подключите ваш GitHub аккаунт

### 3. **Создать репозиторий на GitHub**
```bash
# Создайте новый репозиторий на GitHub
# Название: telegram-signal-bot
# Тип: Public
```

### 4. **Загрузить файлы в GitHub**
```bash
# Инициализируйте git в папке с ботом
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-signal-bot.git
git push -u origin main
```

### 5. **Подключить к Railway**
- В Railway выберите ваш репозиторий
- Railway автоматически определит Python проект
- Нажмите "Deploy Now"

### 6. **Настроить переменные окружения**
В Railway Dashboard:
- Перейдите в раздел "Variables"
- Добавьте переменные:
  - `BOT_TOKEN` = `8351426493:AAEL5tOkQCMGP4aeEyzRqieuspIKR1kgRfA`
  - `PARTNER_LINK` = `https://1wbtqu.life/casino/list?open=register&p=ufc1`
  - `PROMO_CODE` = `AVIATWIN`

### 7. **Проверить работу**
- Railway автоматически перезапустит бота
- Проверьте логи в разделе "Deployments"
- Протестируйте бота в Telegram

## ✅ Результат:
- Бот работает 24/7
- Автоматический перезапуск при ошибках
- Мониторинг и логи
- Бесплатный хостинг

## 🔧 Управление:
- **Логи**: Railway Dashboard → Deployments → View Logs
- **Перезапуск**: Railway Dashboard → Deployments → Redeploy
- **Переменные**: Railway Dashboard → Variables

## 💰 Стоимость:
- **Бесплатно** на Railway (ограничения)
- При превышении лимитов: $5/месяц

## 🎯 Готово!
Ваш бот теперь работает 24/7 и не зависит от вашего ПК! 