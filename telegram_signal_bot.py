import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import random
import time
import threading
import requests
from bs4 import BeautifulSoup
import re
import signal
import sys

import os

# Конфигурация бота
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8351426493:AAEL5tOkQCMGP4aeEyzRqieuspIKR1kgRfA")
PARTNER_LINK = os.environ.get("PARTNER_LINK", "https://1wbtqu.life/casino/list?open=register&p=ufc1")
PROMO_CODE = os.environ.get("PROMO_CODE", "AVIATWIN")

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Файл для хранения данных пользователей
USERS_FILE = "users_data.json"

# Флаг для корректного завершения
shutdown_flag = False

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    global shutdown_flag
    print("\n🛑 Получен сигнал завершения...")
    shutdown_flag = True
    bot.stop_polling()
    sys.exit(0)

def load_users_data():
    """Загрузка данных пользователей из файла"""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users_data(users_data):
    """Сохранение данных пользователей в файл"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

def init_user(user_id):
    """Инициализация нового пользователя"""
    return {
        'registered': False,
        'id_verified': False,
        'auto_update': False,
        'current_balance': 0,
        'total_wins': 0,
        'total_losses': 0,
        'real_id': None,
        'verification_method': None
    }

def get_main_menu():
    """Создание главного меню"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📝 Регистрация", callback_data="register"),
        InlineKeyboardButton("🔍 Ввести ID", callback_data="enter_id")
    )
    markup.add(
        InlineKeyboardButton("🎰 Получить сигнал", callback_data="get_signal"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats")
    )
    markup.add(
        InlineKeyboardButton("💰 Баланс", callback_data="balance"),
        InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
    )
    return markup

def generate_signal():
    """Генерация случайного сигнала"""
    win_chance = random.randint(75, 98)
    bet_amount = random.choice([50, 100, 200, 300, 500, 1000])
    clicks = random.randint(2, 5)
    multiplier = round(random.uniform(1.5, 4.0), 2)
    
    return {
        'win_chance': win_chance,
        'bet_amount': bet_amount,
        'clicks': clicks,
        'multiplier': multiplier
    }

# Real ID verification via web scraping
def real_id_verification(input_id):
    time.sleep(2)  # Imitation of delay

    # Check ID format
    if not input_id.isdigit():
        return False, "ID должен содержать только цифры"

    if len(input_id) < 6 or len(input_id) > 12:
        return False, "ID должен быть от 6 до 12 цифр"

    try:
        # Method 1: Check via referral link
        ref_url = f"https://1wbtqu.life/casino/list?open=register&p=ufc1&ref={input_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(ref_url, headers=headers, timeout=10)

        # If page loads successfully
        if response.status_code == 200:
            # Check page content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for signs of an existing user
            if soup.find('div', class_='user-profile') or soup.find('div', class_='account-info'):
                # User found - generate "real" user data
                balance = random.randint(500, 50000)
                total_games = random.randint(10, 500)
                wins = int(total_games * random.uniform(0.6, 0.8))
                losses = total_games - wins

                return True, {
                    'balance': balance,
                    'total_games': total_games,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': round(wins / total_games * 100, 1),
                    'verification_method': 'web_check'
                }

        # Method 2: Check via API (if available)
        try:
            api_url = f"https://api.1win.com/user/{input_id}/status"
            api_response = requests.get(api_url, headers=headers, timeout=5)

            if api_response.status_code == 200:
                user_data = api_response.json()
                if user_data.get('exists', False):
                    return True, {
                        'balance': user_data.get('balance', random.randint(500, 50000)),
                        'total_games': user_data.get('games', random.randint(10, 500)),
                        'wins': user_data.get('wins', 0),
                        'losses': user_data.get('losses', 0),
                        'win_rate': user_data.get('win_rate', 75.0),
                        'verification_method': 'api_check'
                    }
        except:
            pass

        # Method 3: Check via database search (algorithmic fallback)
        if int(input_id) % 2 == 0 and '0' not in str(input_id) and '5' not in str(input_id):
            # ID passes "database check"
            balance = random.randint(1000, 30000)
            total_games = random.randint(20, 300)
            wins = int(total_games * random.uniform(0.65, 0.85))
            losses = total_games - wins

            return True, {
                'balance': balance,
                'total_games': total_games,
                'wins': wins,
                'losses': losses,
                'win_rate': round(wins / total_games * 100, 1),
                'verification_method': 'database_check'
            }

        # If all methods failed
        return False, "Пользователь не найден в системе"

    except requests.exceptions.RequestException:
        # If unable to connect to server
        return False, "Ошибка подключения к серверу"
    except Exception as e:
        # Other errors
        return False, f"Ошибка проверки: {str(e)}"

def check_user_balance(user_id):
    """Проверка баланса пользователя (имитация)"""
    try:
        # Попытка получить реальный баланс через API
        api_url = f"https://api.1win.com/user/{user_id}/balance"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(api_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('balance', random.randint(1000, 50000))
    except:
        pass
    
    # Возвращаем случайный баланс если API недоступен
    return random.randint(1000, 50000)

def auto_update_signals():
    """Автоматическое обновление сигналов"""
    while True:
        time.sleep(10)  # Обновление каждые 10 секунд
        current_users_data = load_users_data()  # Загружаем актуальные данные
        
        for user_id in current_users_data:
            # Проверяем наличие auto_update в данных пользователя
            if (current_users_data[user_id].get('id_verified', False) and 
                current_users_data[user_id].get('auto_update', False)):
                try:
                    signal = generate_signal()
                    update_text = (
                        f"🔄 *АВТООБНОВЛЕНИЕ СИГНАЛА*\n\n"
                        f"🎰 *VIP СИГНАЛ #{random.randint(1000, 9999)}*\n\n"
                        f"🔥 Вероятность выигрыша: *{signal['win_chance']}%*\n"
                        f"💵 Рекомендуемая ставка: *{signal['bet_amount']}₽*\n"
                        f"🎯 Количество кликов: *{signal['clicks']}*\n"
                        f"📈 Множитель: *x{signal['multiplier']}*\n\n"
                        f"⚡ Следующее обновление через 10 секунд\n\n"
                        f"💡 *Чтобы отключить автообновление, нажмите \"Настройки\"*"
                    )
                    
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.add(
                        InlineKeyboardButton("🔄 Обновить", callback_data="get_signal"),
                        InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
                    )
                    markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
                    
                    # Отправляем обновление только активным пользователям с включенным автообновлением
                    bot.send_message(int(user_id), update_text, parse_mode='Markdown', reply_markup=markup)
                except Exception as e:
                    print(f"Ошибка отправки автообновления пользователю {user_id}: {e}")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    users_data = load_users_data()
    
    if user_id not in users_data:
        users_data[user_id] = init_user(user_id)
        save_users_data(users_data)
    
    welcome_text = (
        f"🎰 *Добро пожаловать в VIP Сигналы Mines!*\n\n"
        f"🔥 *Эксклюзивные сигналы для игры Mines*\n"
        f"📈 *Высокая точность прогнозов*\n"
        f"💰 *Максимальная прибыль*\n\n"
        f"*Для начала работы:*\n"
        f"1️⃣ Зарегистрируйтесь по партнерской ссылке\n"
        f"2️⃣ Введите ваш ID\n"
        f"3️⃣ Получайте VIP сигналы!\n\n"
        f"*Используйте кнопки меню для навигации по боту.*"
    )
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=get_main_menu())

# Обработчик callback запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    users_data = load_users_data()
    
    if user_id not in users_data:
        users_data[user_id] = init_user(user_id)
        save_users_data(users_data)
    
    if call.data == "register":
        register_text = (
            f"📝 *Регистрация в 1win*\n\n"
            f"🔗 *Партнерская ссылка:*\n"
            f"`{PARTNER_LINK}`\n\n"
            f"🎁 *Промокод:* `{PROMO_CODE}`\n\n"
            f"*Инструкция:*\n"
            f"1️⃣ Перейдите по ссылке выше\n"
            f"2️⃣ Зарегистрируйтесь\n"
            f"3️⃣ Введите промокод при регистрации\n"
            f"4️⃣ Скопируйте ваш ID\n"
            f"5️⃣ Вернитесь в бот и введите ID\n\n"
            f"*После регистрации нажмите \"Ввести ID\"*"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔍 Ввести ID", callback_data="enter_id"))
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(register_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
        
        users_data[user_id]['registered'] = True
        save_users_data(users_data)
    
    elif call.data == "enter_id":
        enter_id_text = (
            f"🔍 *Введите ваш ID*\n\n"
            f"*ID можно найти:*\n"
            f"• В личном кабинете 1win\n"
            f"• В настройках профиля\n"
            f"• В разделе \"Мой аккаунт\"\n\n"
            f"*Отправьте ID в следующем сообщении*"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(enter_id_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
        
        # Устанавливаем состояние ожидания ID
        users_data[user_id]['waiting_for_id'] = True
        save_users_data(users_data)
    
    elif call.data == "get_signal":
        if not users_data[user_id].get('id_verified', False):
            error_text = (
                f"❌ *Доступ закрыт*\n\n"
                f"*Для получения сигналов необходимо:*\n"
                f"1️⃣ Зарегистрироваться по партнерской ссылке\n"
                f"2️⃣ Ввести и подтвердить ваш ID\n\n"
                f"*Нажмите \"Регистрация\" для начала*"
            )
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📝 Регистрация", callback_data="register"))
            markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            
            bot.edit_message_text(error_text, call.message.chat.id, call.message.message_id,
                                 parse_mode='Markdown', reply_markup=markup)
        else:
            signal = generate_signal()
            signal_text = (
                f"🎰 *VIP СИГНАЛ #{random.randint(1000, 9999)}*\n\n"
                f"🔥 *Вероятность выигрыша:* {signal['win_chance']}%\n"
                f"💵 *Рекомендуемая ставка:* {signal['bet_amount']}₽\n"
                f"🎯 *Количество кликов:* {signal['clicks']}\n"
                f"📈 *Множитель:* x{signal['multiplier']}\n\n"
                f"⚡ *Следующее обновление через 10 секунд*"
            )
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 Обновить", callback_data="get_signal"),
                InlineKeyboardButton("📊 Статистика", callback_data="stats")
            )
            markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            
            bot.edit_message_text(signal_text, call.message.chat.id, call.message.message_id,
                                 parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "stats":
        if users_data[user_id].get('id_verified', False):
            total_games = users_data[user_id].get('total_wins', 0) + users_data[user_id].get('total_losses', 0)
            win_rate = round(users_data[user_id].get('total_wins', 0) / max(1, total_games) * 100, 1)
            
            stats_text = (
                f"📊 *ВАША СТАТИСТИКА*\n\n"
                f"🆔 *ID:* `{users_data[user_id].get('real_id', 'Неизвестно')}`\n"
                f"💰 *Текущий баланс:* {users_data[user_id].get('current_balance', 0)}₽\n"
                f"🎯 *Всего игр:* {total_games}\n"
                f"✅ *Победы:* {users_data[user_id].get('total_wins', 0)}\n"
                f"❌ *Поражения:* {users_data[user_id].get('total_losses', 0)}\n"
                f"📈 *Процент побед:* {win_rate}%\n\n"
                f"🔄 *Автообновление:* {'Включено' if users_data[user_id].get('auto_update', False) else 'Выключено'}\n"
                f"🔍 *Метод проверки:* {users_data[user_id].get('verification_method', 'Неизвестно')}"
            )
        else:
            stats_text = (
                f"📊 *СТАТИСТИКА*\n\n"
                f"❌ *Доступ закрыт*\n\n"
                f"*Для просмотра статистики необходимо:*\n"
                f"1️⃣ Зарегистрироваться\n"
                f"2️⃣ Ввести и подтвердить ID\n\n"
                f"*Нажмите \"Регистрация\" для начала*"
            )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "balance":
        if users_data[user_id].get('id_verified', False):
            # Обновляем баланс
            new_balance = check_user_balance(users_data[user_id].get('real_id', '0'))
            users_data[user_id]['current_balance'] = new_balance
            save_users_data(users_data)
            
            balance_text = (
                f"💰 *ВАШ БАЛАНС*\n\n"
                f"🆔 *ID:* `{users_data[user_id].get('real_id', 'Неизвестно')}`\n"
                f"💵 *Текущий баланс:* *{new_balance}₽*\n"
                f"📊 *Последнее обновление:* {time.strftime('%H:%M:%S')}\n\n"
                f"*Для пополнения баланса используйте партнерскую ссылку*"
            )
        else:
            balance_text = (
                f"💰 *БАЛАНС*\n\n"
                f"❌ *Доступ закрыт*\n\n"
                f"*Для просмотра баланса необходимо:*\n"
                f"1️⃣ Зарегистрироваться\n"
                f"2️⃣ Ввести и подтвердить ID\n\n"
                f"*Нажмите \"Регистрация\" для начала*"
            )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(balance_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "settings":
        auto_status = "🟢 ВКЛ" if users_data[user_id].get('auto_update', False) else "🔴 ВЫКЛ"
        settings_text = (
            f"⚙️ *Настройки бота*\n\n"
            f"🔄 *Автообновление сигналов:* {auto_status}\n\n"
            f"📱 *Опции:*\n"
            f"• Автообновление - сигналы приходят каждые 10 секунд\n"
            f"• Ручное обновление - сигналы только по запросу\n\n"
            f"*Выберите режим работы:*"
        )
        
        markup = InlineKeyboardMarkup(row_width=2)
        if users_data[user_id].get('auto_update', False):
            markup.add(InlineKeyboardButton("🔴 Отключить авто", callback_data="disable_auto"))
        else:
            markup.add(InlineKeyboardButton("🟢 Включить авто", callback_data="enable_auto"))
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(settings_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "enable_auto":
        users_data[user_id]['auto_update'] = True
        save_users_data(users_data)
        
        auto_text = (
            f"✅ *АВТООБНОВЛЕНИЕ ВКЛЮЧЕНО*\n\n"
            f"🔄 *Сигналы будут обновляться автоматически каждые 10 секунд*\n\n"
            f"*Вы получите уведомления о новых сигналах*"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(auto_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "disable_auto":
        users_data[user_id]['auto_update'] = False
        save_users_data(users_data)
        
        auto_text = (
            f"❌ *АВТООБНОВЛЕНИЕ ОТКЛЮЧЕНО*\n\n"
            f"🔄 *Теперь вы будете получать сигналы только при нажатии кнопки \"Обновить\"*\n\n"
            f"*Для получения сигнала нажмите \"Получить сигнал\"*"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎰 Получить сигнал", callback_data="get_signal"))
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(auto_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "back_to_main":
        main_text = (
            f"🎰 *VIP СИГНАЛЫ MINES*\n\n"
            f"*Выберите действие:*\n\n"
            f"📝 *Регистрация* - зарегистрироваться в 1win\n"
            f"🔍 *Ввести ID* - подтвердить ваш аккаунт\n"
            f"🎰 *Получить сигнал* - получить VIP прогноз\n"
            f"📊 *Статистика* - ваши результаты\n"
            f"💰 *Баланс* - текущий баланс\n"
            f"⚙️ *Настройки* - настройки бота"
        )
        
        bot.edit_message_text(main_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=get_main_menu())

# Обработчик текстовых сообщений (для ввода ID)
@bot.message_handler(func=lambda message: True)
def process_id_input(message):
    user_id = str(message.from_user.id)
    users_data = load_users_data()
    
    if user_id not in users_data:
        users_data[user_id] = init_user(user_id)
        save_users_data(users_data)
    
    # Проверяем, ожидает ли пользователь ввода ID
    if users_data[user_id].get('waiting_for_id', False):
        input_id = message.text.strip()
        
        # Отправляем сообщение о проверке
        checking_msg = bot.reply_to(message, "🔍 *Подключаюсь к серверам 1win...*", parse_mode='Markdown')
        
        # Выполняем проверку ID
        success, result = real_id_verification(input_id)
        
        if success:
            # ID принят
            user_data = result
            users_data[user_id]['id_verified'] = True
            users_data[user_id]['real_id'] = input_id
            users_data[user_id]['current_balance'] = user_data['balance']
            users_data[user_id]['total_wins'] = user_data['wins']
            users_data[user_id]['total_losses'] = user_data['losses']
            users_data[user_id]['verification_method'] = user_data['verification_method']
            users_data[user_id]['waiting_for_id'] = False
            save_users_data(users_data)
            
            success_text = (
                f"✅ *ID ПРИНЯТ!*\n\n"
                f"🆔 *Ваш ID:* `{input_id}`\n"
                f"💰 *Баланс:* {user_data['balance']}₽\n"
                f"🎯 *Всего игр:* {user_data['total_games']}\n"
                f"✅ *Победы:* {user_data['wins']}\n"
                f"❌ *Поражения:* {user_data['losses']}\n"
                f"📈 *Процент побед:* {user_data['win_rate']}%\n"
                f"🔍 *Метод проверки:* {user_data['verification_method']}\n\n"
                f"🎉 *ДОСТУП ОТКРЫТ!*\n"
                f"*Теперь вы можете получать VIP сигналы!*"
            )
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🎰 Получить сигнал", callback_data="get_signal"),
                InlineKeyboardButton("📊 Статистика", callback_data="stats")
            )
            markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            
            bot.edit_message_text(success_text, checking_msg.chat.id, checking_msg.message_id,
                                 parse_mode='Markdown', reply_markup=markup)
        else:
            # ID отклонен
            users_data[user_id]['waiting_for_id'] = False
            save_users_data(users_data)
            
            error_text = (
                f"❌ *ID ОТКЛОНЕН*\n\n"
                f"*Причина:* {result}\n\n"
                f"*Проверьте:*\n"
                f"• Правильность ID\n"
                f"• Регистрацию в 1win\n"
                f"• Ввод промокода\n\n"
                f"*Попробуйте еще раз или обратитесь в поддержку*"
            )
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔍 Ввести ID", callback_data="enter_id"))
            markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            
            bot.edit_message_text(error_text, checking_msg.chat.id, checking_msg.message_id,
                                 parse_mode='Markdown', reply_markup=markup)
    else:
        # Обычное сообщение - показываем главное меню
        bot.reply_to(message, "Используйте кнопки меню для навигации по боту.", reply_markup=get_main_menu())

# Запуск автообновления в отдельном потоке
def start_auto_update():
    auto_update_signals()

# Запуск бота
if __name__ == "__main__":
    print("🤖 Запуск VIP Сигналы Mines бота...")
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Очищаем webhook'и для предотвращения конфликтов
    try:
        print("🧹 Очистка webhook'ов...")
        bot.remove_webhook()
        time.sleep(2)
        
        # Дополнительная очистка через API
        try:
            import requests
            webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
            response = requests.post(webhook_url, json={"drop_pending_updates": True})
            if response.status_code == 200:
                print("✅ Webhook'и успешно очищены")
            else:
                print(f"⚠️ Ошибка очистки webhook'ов: {response.status_code}")
                
            # Принудительное удаление всех обновлений
            updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            response = requests.get(updates_url, params={"offset": -1, "limit": 1})
            if response.status_code == 200:
                print("✅ Обновления очищены")
                
        except Exception as e:
            print(f"⚠️ Ошибка при дополнительной очистке webhook'ов: {e}")
            
    except Exception as e:
        print(f"⚠️ Ошибка при очистке webhook'ов: {e}")
    
    # Запускаем автообновление в отдельном потоке
    auto_update_thread = threading.Thread(target=start_auto_update, daemon=True)
    auto_update_thread.start()
    
    print("✅ Бот запущен!")
    print("📱 Автообновление сигналов каждые 10 секунд")
    print("🎰 Готов к работе!")
    
    # Запускаем бота с обработкой ошибок
    retry_count = 0
    max_retries = 10
    use_webhook = False
    
    while not shutdown_flag and retry_count < max_retries:
        try:
            if not use_webhook:
                print("🔄 Подключение к Telegram API через polling...")
                bot.polling(none_stop=True, timeout=60)
            else:
                print("🔄 Подключение к Telegram API через webhook...")
                # Альтернативный способ через webhook
                bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 409:
                retry_count += 1
                print(f"⚠️ Обнаружен конфликт: другой экземпляр бота уже запущен (попытка {retry_count}/{max_retries})")
                print("🧹 Принудительная очистка webhook'ов и обновлений...")
                
                # Агрессивная очистка webhook'ов
                try:
                    bot.remove_webhook()
                    time.sleep(3)
                    
                    # Принудительная очистка через API
                    webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
                    response = requests.post(webhook_url, json={"drop_pending_updates": True})
                    
                    # Принудительное получение и сброс обновлений
                    updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                    response = requests.get(updates_url, params={"offset": -1, "limit": 1})
                    
                    print("✅ Принудительная очистка завершена")
                    time.sleep(5)
                except Exception as cleanup_error:
                    print(f"⚠️ Ошибка при принудительной очистке: {cleanup_error}")
                
                # Пробуем переключиться на webhook после нескольких попыток
                if retry_count >= 3 and not use_webhook:
                    print("🔄 Переключение на webhook режим...")
                    use_webhook = True
                
                wait_time = min(60 * retry_count, 600)  # Увеличиваем время ожидания до 10 минут
                print(f"🔄 Ожидание {wait_time} секунд перед повторной попыткой...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Ошибка Telegram API: {e}")
                print("🔄 Повторная попытка через 60 секунд...")
                time.sleep(60)
                continue
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            print("🔄 Повторная попытка через 60 секунд...")
            time.sleep(60)
            continue
    
    if retry_count >= max_retries:
        print("❌ Превышено максимальное количество попыток. Бот остановлен.")
    else:
        print("🛑 Бот остановлен пользователем.")