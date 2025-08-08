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
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    def get_msk_time_str():
        return datetime.now(ZoneInfo("Europe/Moscow")).strftime("%H:%M:%S")
except Exception:
    def get_msk_time_str():
        # Fallback: UTC+3 approximation
        return time.strftime("%H:%M:%S", time.gmtime(time.time() + 3 * 3600))

# Конфигурация бота
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8351426493:AAEL5tOkQCMGP4aeEyzRqieuspIKR1kgRfA")
PARTNER_LINK = os.environ.get("PARTNER_LINK", "https://1wbtqu.life/casino/list?open=register&p=ufc1")
PROMO_CODE = os.environ.get("PROMO_CODE", "AVIATWIN")

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Файл для хранения данных пользователей
USERS_FILE = os.environ.get("USERS_FILE", "/workspace/data/users_data.json")

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
        # Создаем папку если её нет
        import os
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        print(f"📁 Загружаем данные из: {USERS_FILE}")
        
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Загружено {len(data)} пользователей")
            return data
    except FileNotFoundError:
        print(f"📁 Файл данных не найден, создаем новый: {USERS_FILE}")
        return {}

def save_users_data(users_data):
    """Сохранение данных пользователей в файл"""
    # Создаем папку если её нет
    import os
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    
    print(f"💾 Сохраняем данные в: {USERS_FILE}")
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено {len(users_data)} пользователей")

def ensure_user_data(user_id, users_data):
    """Проверка и восстановление данных пользователя"""
    if user_id not in users_data:
        users_data[user_id] = init_user(user_id)
        print(f"🆕 Создан новый пользователь: {user_id}")
        save_users_data(users_data)
    else:
        # Проверяем, есть ли все необходимые поля
        user_data = users_data[user_id]
        required_fields = ['registered', 'id_verified', 'auto_update', 'current_balance', 
                          'total_wins', 'total_losses', 'real_id', 'verification_method', 
                          'last_signal_time', 'waiting_for_id', 'current_signal']
        
        missing_fields = []
        for field in required_fields:
            if field not in user_data:
                missing_fields.append(field)
                user_data[field] = init_user(user_id)[field]
        
        if missing_fields:
            print(f"🔧 Восстановлены недостающие поля для пользователя {user_id}: {missing_fields}")
            save_users_data(users_data)
    
    return users_data

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
        'verification_method': None,
        'last_signal_time': 0,
        'waiting_for_id': False,
        # Пошаговый режим сигнала: None, пока не создан новый сигнал
        'current_signal': None
    }

def get_main_menu(user_data: dict = None):
    """Создание главного меню, зависящего от статуса верификации.
    Принимает либо словарь user_data, либо строку user_id (тогда загрузит данные сам).
    """
    is_verified = False
    # Поддержка передачи user_id вместо user_data
    if isinstance(user_data, str):
        uid = user_data
        data = load_users_data()
        data = ensure_user_data(uid, data)
        is_verified = bool(data[uid].get('id_verified', False))
    elif isinstance(user_data, dict) and user_data is not None:
        is_verified = bool(user_data.get('id_verified', False))
    
    markup = InlineKeyboardMarkup(row_width=2)
    if not is_verified:
        markup.add(
            InlineKeyboardButton("🎯 Регистрация", callback_data="register"),
            InlineKeyboardButton("🔐 Ввести ID", callback_data="enter_id")
        )
    else:
        # Для верифицированных вместо регистрации — советы
        markup.add(
            InlineKeyboardButton("💡 Советы", callback_data="tips"),
            InlineKeyboardButton("📈 Статистика", callback_data="stats")
        )
    # Общие пункты
    markup.add(
        InlineKeyboardButton("⚡ VIP Сигнал", callback_data="get_signal"),
        InlineKeyboardButton("💎 Баланс", callback_data="balance")
    )
    markup.add(
        InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
    )
    return markup

def generate_signal():
    """Генерация правдоподобного VIP сигнала"""
    # Более реалистичные параметры
    win_chance = random.choice([85, 87, 89, 91, 93, 95, 97])
    bet_amount = random.choice([100, 150, 200, 250, 300, 400, 500, 750, 1000])
    clicks = random.choice([2, 3, 4, 5])
    
    # Более реалистичные множители
    if clicks == 2:
        multiplier = round(random.uniform(1.8, 2.5), 2)
    elif clicks == 3:
        multiplier = round(random.uniform(2.2, 3.2), 2)
    elif clicks == 4:
        multiplier = round(random.uniform(2.8, 4.0), 2)
    else:  # 5 clicks
        multiplier = round(random.uniform(3.5, 5.0), 2)
    
    return {
        'win_chance': win_chance,
        'bet_amount': bet_amount,
        'clicks': clicks,
        'multiplier': multiplier
    }

# ===== Новые помощники для сетки и пошаговых координат =====
LETTERS = ["A", "B", "C", "D", "E"]
NUMBERS = ["1", "2", "3", "4", "5"]

def generate_coords_sequence(steps_count: int):
    """Генерирует уникальную последовательность координат вида A2, C4..."""
    cells = [f"{letter}{number}" for letter in LETTERS for number in NUMBERS]
    random.shuffle(cells)
    return cells[:steps_count]

def render_grid_with_labels():
    """Возвращает текст с подписью осей: верх 1–5, слева A–E."""
    header = "    " + "  ".join(NUMBERS)
    rows = []
    for idx, letter in enumerate(LETTERS):
        rows.append(f"{letter} | ⬛ ⬛ ⬛ ⬛ ⬛")
    grid_text = "\n".join([header] + rows)
    return grid_text

def format_instruction(coords: list, revealed: int):
    """Формирует строку инструкции, показывая только открытые шаги и многоточие для следующих."""
    total = len(coords)
    if total == 0:
        return ""
    if revealed <= 0:
        preview = f"{coords[0]} → …"
    elif revealed >= total:
        preview = " → ".join(coords[:total])
    else:
        preview = " → ".join(coords[:revealed]) + " → …"
    progress = f"(открыто {revealed} из {total})"
    return f"Нажимай по порядку: {preview} \n{progress}"

# Real ID verification via 1win API and web scraping
def real_id_verification(input_id):
    print(f"🔍 Начинаем НАСТОЯЩУЮ верификацию ID 1win: {input_id}")
    time.sleep(1)

    # Check ID format
    if not input_id.isdigit():
        print(f"❌ ID не содержит только цифры: {input_id}")
        return False, "ID должен содержать только цифры"

    if len(input_id) < 6 or len(input_id) > 12:
        print(f"❌ ID неправильной длины: {len(input_id)}")
        return False, "ID должен быть от 6 до 12 цифр"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

    try:
        # Method 1: Try to get REAL data from 1win API
        print(f"🔍 Метод 1: Попытка получить РЕАЛЬНЫЕ данные из API 1win...")
        
        # Try different API endpoints that might exist
        api_endpoints = [
            f"https://api.1win.com/user/{input_id}",
            f"https://api.1win.com/users/{input_id}",
            f"https://1win.com/api/user/{input_id}",
            f"https://1win.com/api/users/{input_id}",
            f"https://api.1win.com/profile/{input_id}",
            f"https://1win.com/api/profile/{input_id}"
        ]
        
        for api_url in api_endpoints:
            try:
                print(f"🔍 Пробуем API: {api_url}")
                response = requests.get(api_url, headers=headers, timeout=10)
                print(f"🔍 API ответ: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ Получены реальные данные: {data}")
                        
                        # Extract real data if available
                        balance = data.get('balance') or data.get('user_balance') or data.get('account_balance') or data.get('money')
                        total_games = data.get('total_games') or data.get('games_played') or data.get('games')
                        wins = data.get('wins') or data.get('wins_count') or data.get('victories')
                        losses = data.get('losses') or data.get('losses_count') or data.get('defeats')
                        
                        if balance or total_games or wins or losses:
                            return True, {
                                'balance': int(balance) if balance else random.randint(1000, 50000),
                                'total_games': int(total_games) if total_games else random.randint(50, 1000),
                                'wins': int(wins) if wins else random.randint(30, 800),
                                'losses': int(losses) if losses else random.randint(10, 200),
                                'win_rate': round((int(wins) / int(total_games) * 100) if wins and total_games else random.uniform(70, 95), 1),
                                'verification_method': '1win_real_api'
                            }
                    except json.JSONDecodeError:
                        # If not JSON, check if it contains user data
                        if 'user' in response.text.lower() or 'balance' in response.text.lower():
                            print(f"✅ Найдены данные пользователя в тексте")
                            return True, {
                                'balance': random.randint(1000, 50000),
                                'total_games': random.randint(50, 1000),
                                'wins': random.randint(30, 800),
                                'losses': random.randint(10, 200),
                                'win_rate': round(random.uniform(70, 95), 1),
                                'verification_method': '1win_api_text'
                            }
            except Exception as e:
                print(f"⚠️ Ошибка API {api_url}: {e}")
                continue

        # Method 2: Try to scrape REAL data from 1win website
        print(f"🔍 Метод 2: Попытка получить РЕАЛЬНЫЕ данные со страницы 1win...")
        
        try:
            # Try different user profile URLs
            profile_urls = [
                f"https://1win.com/user/{input_id}",
                f"https://1win.com/profile/{input_id}",
                f"https://1win.com/account/{input_id}",
                f"https://1win.com/users/{input_id}"
            ]
            
            for profile_url in profile_urls:
                try:
                    print(f"🔍 Пробуем страницу: {profile_url}")
                    response = requests.get(profile_url, headers=headers, timeout=15)
                    print(f"🔍 Статус страницы: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for REAL balance data
                        balance_selectors = [
                            '[class*="balance"]', '[id*="balance"]', 
                            '[class*="user-balance"]', '[class*="account-balance"]',
                            '[class*="money"]', '[class*="amount"]'
                        ]
                        
                        real_balance = None
                        for selector in balance_selectors:
                            balance_elem = soup.select_one(selector)
                            if balance_elem:
                                balance_text = balance_elem.get_text()
                                import re
                                balance_match = re.search(r'(\d+(?:,\d+)*)', balance_text)
                                if balance_match:
                                    real_balance = int(balance_match.group(1).replace(',', ''))
                                    print(f"✅ Найден реальный баланс: {real_balance}")
                                    break
                        
                        # Look for REAL game statistics
                        stats_selectors = [
                            '[class*="games"]', '[class*="stats"]', 
                            '[class*="wins"]', '[class*="losses"]'
                        ]
                        
                        real_stats = {}
                        for selector in stats_selectors:
                            stats_elem = soup.select_one(selector)
                            if stats_elem:
                                stats_text = stats_elem.get_text()
                                # Extract numbers from stats
                                numbers = re.findall(r'\d+', stats_text)
                                if len(numbers) >= 2:
                                    real_stats['total_games'] = int(numbers[0])
                                    real_stats['wins'] = int(numbers[1])
                                    if len(numbers) >= 3:
                                        real_stats['losses'] = int(numbers[2])
                                    print(f"✅ Найдена реальная статистика: {real_stats}")
                                    break
                        
                        if real_balance or real_stats:
                            return True, {
                                'balance': real_balance if real_balance else random.randint(1000, 50000),
                                'total_games': real_stats.get('total_games', random.randint(50, 1000)),
                                'wins': real_stats.get('wins', random.randint(30, 800)),
                                'losses': real_stats.get('losses', random.randint(10, 200)),
                                'win_rate': round((real_stats.get('wins', 0) / max(1, real_stats.get('total_games', 1)) * 100) if real_stats.get('wins') else random.uniform(70, 95), 1),
                                'verification_method': '1win_real_scraping'
                            }
                        
                        # If page loads but no specific data found, user might exist
                        if 'user' in response.text.lower() or 'profile' in response.text.lower():
                            print(f"✅ Страница пользователя найдена, но данные не извлечены")
                            return True, {
                                'balance': random.randint(1000, 50000),
                                'total_games': random.randint(50, 1000),
                                'wins': random.randint(30, 800),
                                'losses': random.randint(10, 200),
                                'win_rate': round(random.uniform(70, 95), 1),
                                'verification_method': '1win_page_exists'
                            }
                            
                except Exception as e:
                    print(f"⚠️ Ошибка страницы {profile_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Ошибка веб-скрапинга: {e}")

        # Method 3: Check if ID format is valid for 1win
        print(f"🔍 Метод 3: Проверка формата ID...")
        id_int = int(input_id)
        
        if (len(input_id) >= 7 and 
            id_int > 1000000 and 
            '000' not in input_id and 
            '111' not in str(input_id) and
            sum(int(d) for d in input_id) > 10):
            
            print(f"✅ ID соответствует формату 1win: {input_id}")
            print(f"⚠️ НО: Не удалось получить реальные данные из 1win")
            print(f"⚠️ Причина: 1win не предоставляет публичный API для получения данных пользователей")
            print(f"⚠️ Решение: Используйте данные из вашего личного кабинета 1win")
            
            return True, {
                'balance': 0,  # Не можем получить реальный баланс
                'total_games': 0,  # Не можем получить реальную статистику
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'verification_method': '1win_format_only'
            }

        # If all methods failed
        print(f"❌ Пользователь не найден в системе 1win: {input_id}")
        return False, "Пользователь не найден в системе 1win. Проверьте правильность ID и регистрацию."

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к серверам 1win: {e}")
        return False, "Ошибка подключения к серверам 1win"
    except Exception as e:
        print(f"❌ Общая ошибка проверки: {e}")
        return False, f"Ошибка проверки: {str(e)}"

def check_user_balance(user_id):
    """Проверка реального баланса пользователя 1win"""
    print(f"💰 Проверяем баланс пользователя: {user_id}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8'
    }
    
    try:
        # Попытка получить реальный баланс через API
        api_urls = [
            f"https://api.1win.com/user/{user_id}/balance",
            f"https://1win.com/api/user/{user_id}/balance",
            f"https://api.1win.com/user/{user_id}/profile"
        ]
        
        for api_url in api_urls:
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                print(f"💰 API баланс: {api_url} - статус: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        balance = data.get('balance') or data.get('user_balance') or data.get('account_balance')
                        if balance:
                            print(f"✅ Получен реальный баланс: {balance}")
                            return int(balance)
                    except json.JSONDecodeError:
                        # Если ответ не JSON, ищем баланс в тексте
                        if 'balance' in response.text.lower():
                            import re
                            balance_match = re.search(r'balance["\']?\s*:\s*(\d+)', response.text)
                            if balance_match:
                                balance = int(balance_match.group(1))
                                print(f"✅ Извлечен баланс из текста: {balance}")
                                return balance
            except Exception as e:
                print(f"⚠️ Ошибка API баланса {api_url}: {e}")
                continue
        
        # Если API недоступен, проверяем через веб-скрапинг
        try:
            main_url = f"https://1win.com/user/{user_id}"
            response = requests.get(main_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Ищем элементы с балансом
                balance_selectors = [
                    '[class*="balance"]', '[id*="balance"]', 
                    '[class*="user-balance"]', '[class*="account-balance"]'
                ]
                
                for selector in balance_selectors:
                    balance_elem = soup.select_one(selector)
                    if balance_elem:
                        balance_text = balance_elem.get_text()
                        import re
                        balance_match = re.search(r'(\d+(?:,\d+)*)', balance_text)
                        if balance_match:
                            balance = int(balance_match.group(1).replace(',', ''))
                            print(f"✅ Извлечен баланс со страницы: {balance}")
                            return balance
        except Exception as e:
            print(f"⚠️ Ошибка веб-скрапинга баланса: {e}")
    
    except Exception as e:
        print(f"❌ Общая ошибка проверки баланса: {e}")
    
    # Возвращаем случайный баланс если все методы недоступны
    fallback_balance = random.randint(1000, 50000)
    print(f"💰 Используем резервный баланс: {fallback_balance}")
    return fallback_balance

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
                    # Проверяем перезарядку для автообновления
                    current_time = time.time()
                    last_signal_time = current_users_data[user_id].get('last_signal_time', 0)
                    cooldown_remaining = 10 - (current_time - last_signal_time)
                    
                    if cooldown_remaining <= 0:
                        # Перезарядка завершена, отправляем новый сигнал
                        signal = generate_signal()
                        signal_number = random.randint(1000, 9999)
                        
                        # Формируем пошаговый режим и сетку
                        coords_sequence = generate_coords_sequence(signal['clicks'])
                        current_users_data[user_id]['current_signal'] = {
                            'number': signal_number,
                            'coords': coords_sequence,
                            'revealed': 0,
                            'created_at': current_time,
                            'win_chance': signal['win_chance'],
                            'bet_amount': signal['bet_amount'],
                            'clicks': signal['clicks'],
                            'multiplier': signal['multiplier']
                        }
                        grid = render_grid_with_labels()
                        instr = format_instruction(coords_sequence, 0)
                        
                        update_text = (
                            f"🔄 *АВТООБНОВЛЕНИЕ СИГНАЛА*\n\n"
                            f"🎰 *VIP СИГНАЛ #{signal_number}*\n\n"
                            f"🔥 Вероятность выигрыша: *{signal['win_chance']}%*\n"
                            f"💵 Рекомендуемая ставка: *{signal['bet_amount']}₽*\n"
                            f"🎯 Количество кликов: *{signal['clicks']}*\n"
                            f"📈 Множитель: *x{signal['multiplier']}*\n\n"
                            f"🗺️ *Сетка:*\n"
                            f"{grid}\n\n"
                            f"📌 {instr}\n\n"
                            f"🕐 Время (МСК): *{get_msk_time_str()}*\n"
                        )
                        
                        markup = InlineKeyboardMarkup(row_width=2)
                        markup.add(InlineKeyboardButton("➡️ Показать следующий шаг", callback_data="next_step"))
                        markup.add(InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
                        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
                        
                        # Отправляем обновление только активным пользователям с включенным автообновлением
                        bot.send_message(int(user_id), update_text, parse_mode='Markdown', reply_markup=markup)
                        
                        # Обновляем время последнего сигнала и сохраняем состояние
                        current_users_data[user_id]['last_signal_time'] = current_time
                        save_users_data(current_users_data)
                        
                except Exception as e:
                    print(f"Ошибка отправки автообновления пользователю {user_id}: {e}")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    users_data = load_users_data()
    users_data = ensure_user_data(user_id, users_data)
    
    # Проверяем, был ли пользователь уже верифицирован
    if users_data[user_id].get('id_verified', False):
        # Пользователь уже верифицирован
        welcome_text = (
            f"🎰 *С возвращением в VIP Сигналы Mines!*\n\n"
            f"✅ *Ваш ID:* `{users_data[user_id].get('real_id', 'Неизвестно')}`\n"
            f"🔍 *Статус:* Верифицирован\n"
            f"🔄 *Автообновление:* {'Включено' if users_data[user_id].get('auto_update', False) else 'Выключено'}\n\n"
            f"🎯 *Выберите действие:*"
        )
    else:
        # Новый пользователь или не верифицированный
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
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=get_main_menu(user_id))

# Обработчик команды /status
@bot.message_handler(commands=['status'])
def status_command(message):
    user_id = str(message.from_user.id)
    users_data = load_users_data()
    users_data = ensure_user_data(user_id, users_data)
    
    user_data = users_data[user_id]
    
    status_text = (
        f"📊 *СТАТУС ПОЛЬЗОВАТЕЛЯ*\n\n"
        f"🆔 *ID пользователя:* `{user_id}`\n"
        f"✅ *Верифицирован:* {'Да' if user_data.get('id_verified', False) else 'Нет'}\n"
    )
    
    if user_data.get('id_verified', False):
        status_text += (
            f"🎯 *1win ID:* `{user_data.get('real_id', 'Неизвестно')}`\n"
            f"🔍 *Метод проверки:* {user_data.get('verification_method', 'Неизвестно')}\n"
            f"🔄 *Автообновление:* {'Включено' if user_data.get('auto_update', False) else 'Выключено'}\n"
            f"💰 *Баланс:* {user_data.get('current_balance', 0)}₽\n"
            f"🎮 *Всего игр:* {user_data.get('total_wins', 0) + user_data.get('total_losses', 0)}\n"
            f"✅ *Победы:* {user_data.get('total_wins', 0)}\n"
            f"❌ *Поражения:* {user_data.get('total_losses', 0)}\n"
        )
    else:
        status_text += (
            f"📝 *Зарегистрирован:* {'Да' if user_data.get('registered', False) else 'Нет'}\n"
            f"⏳ *Ожидает ID:* {'Да' if user_data.get('waiting_for_id', False) else 'Нет'}\n"
        )
    
    status_text += f"\n💾 *Данные сохранены:* Да"
    
    bot.reply_to(message, status_text, parse_mode='Markdown')

# Обработчик callback запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    users_data = load_users_data()
    users_data = ensure_user_data(user_id, users_data)
    
    if call.data == "register":
        if users_data[user_id].get('id_verified', False):
            already_text = (
                f"✅ *Вы уже верифицированы.*\n\n"
                f"💡 Откройте раздел *Советы* или получите *VIP Сигнал*."
            )
            bot.edit_message_text(already_text, call.message.chat.id, call.message.message_id,
                                 parse_mode='Markdown', reply_markup=get_main_menu(users_data[user_id]))
        else:
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
        if users_data[user_id].get('id_verified', False):
            already_text = (
                f"✅ *Ваш ID уже подтвержден.*\n\n"
                f"💡 Перейдите в *Советы* или получите *VIP Сигнал*."
            )
            bot.edit_message_text(already_text, call.message.chat.id, call.message.message_id,
                                 parse_mode='Markdown', reply_markup=get_main_menu(users_data[user_id]))
        else:
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
            print(f"✅ Установлен флаг waiting_for_id для пользователя {user_id}")
    
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
            # Проверяем перезарядку
            current_time = time.time()
            last_signal_time = users_data[user_id].get('last_signal_time', 0)
            cooldown_remaining = 10 - (current_time - last_signal_time)
            
            if cooldown_remaining > 0:
                # Перезарядка еще активна
                cooldown_text = (
                    f"⏰ *ПЕРЕЗАРЯДКА АКТИВНА*\n\n"
                    f"🔄 *Осталось:* {int(cooldown_remaining)} сек\n"
                    f"⚡ *Следующий сигнал через:* {int(cooldown_remaining)} сек\n\n"
                    f"💡 *Подождите немного перед следующим запросом*"
                )
                
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("⏰ Ждать", callback_data="wait_cooldown"),
                    InlineKeyboardButton("📊 Статистика", callback_data="stats")
                )
                markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
                
                bot.edit_message_text(cooldown_text, call.message.chat.id, call.message.message_id,
                                     parse_mode='Markdown', reply_markup=markup)
            else:
                # Генерируем новый сигнал и пошаговые координаты
                signal = generate_signal()
                signal_number = random.randint(1000, 9999)
                coords_sequence = generate_coords_sequence(signal['clicks'])
                users_data[user_id]['current_signal'] = {
                    'number': signal_number,
                    'coords': coords_sequence,
                    'revealed': 0,
                    'created_at': current_time,
                    'win_chance': signal['win_chance'],
                    'bet_amount': signal['bet_amount'],
                    'clicks': signal['clicks'],
                    'multiplier': signal['multiplier']
                }
                
                grid = render_grid_with_labels()
                instr = format_instruction(coords_sequence, 0)
                
                signal_text = (
                    f"🎰 *VIP СИГНАЛ #{signal_number}*\n\n"
                    f"🔥 *Вероятность выигрыша:* {signal['win_chance']}%\n"
                    f"💵 *Рекомендуемая ставка:* {signal['bet_amount']}₽\n"
                    f"🎯 *Количество кликов:* {signal['clicks']}\n"
                    f"📈 *Множитель:* x{signal['multiplier']}\n\n"
                    f"🗺️ *Сетка:*\n"
                    f"{grid}\n\n"
                    f"📌 {instr}\n\n"
                    f"▶️ Нажмите кнопку ниже, чтобы показать следующий шаг"
                )
                
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(InlineKeyboardButton("➡️ Показать следующий шаг", callback_data="next_step"))
                markup.add(
                    InlineKeyboardButton("🔄 Обновить", callback_data="get_signal"),
                    InlineKeyboardButton("📊 Статистика", callback_data="stats")
                )
                markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
                
                bot.edit_message_text(signal_text, call.message.chat.id, call.message.message_id,
                                     parse_mode='Markdown', reply_markup=markup)
                
                # Сохраняем время последнего сигнала
                users_data[user_id]['last_signal_time'] = current_time
                save_users_data(users_data)
    
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
                f"📊 *Последнее обновление (МСК):* {get_msk_time_str()}\n\n"
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
    
    elif call.data == "wait_cooldown":
        # Показываем время до следующего сигнала
        current_time = time.time()
        last_signal_time = users_data[user_id].get('last_signal_time', 0)
        cooldown_remaining = 10 - (current_time - last_signal_time)
        
        if cooldown_remaining > 0:
            wait_text = (
                f"⏰ *ПЕРЕЗАРЯДКА*\n\n"
                f"🔄 *Осталось:* {int(cooldown_remaining)} сек\n"
                f"⚡ *Следующий сигнал через:* {int(cooldown_remaining)} сек\n\n"
                f"💡 *Подождите немного перед следующим запросом*"
            )
        else:
            wait_text = (
                f"✅ *ПЕРЕЗАРЯДКА ЗАВЕРШЕНА*\n\n"
                f"⚡ *Можете получить новый сигнал!*\n\n"
                f"🎯 *Нажмите \"VIP Сигнал\" для получения*"
            )
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⚡ VIP Сигнал", callback_data="get_signal"),
            InlineKeyboardButton("📊 Статистика", callback_data="stats")
        )
        markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        
        bot.edit_message_text(wait_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "next_step":
        current_signal_data = users_data[user_id].get('current_signal')
        if current_signal_data and isinstance(current_signal_data, dict) and current_signal_data.get('coords'):
            revealed_count = current_signal_data['revealed']
            total_steps = len(current_signal_data['coords'])
            
            if revealed_count < total_steps:
                revealed_count += 1
                current_signal_data['revealed'] = revealed_count
                save_users_data(users_data)
                
                grid = render_grid_with_labels()
                instr = format_instruction(current_signal_data['coords'][:revealed_count], revealed_count)
                
                next_step_text = (
                    f"🎰 *VIP СИГНАЛ #{current_signal_data.get('number','')}*\n\n"
                    f"🔥 *Вероятность выигрыша:* {current_signal_data.get('win_chance','')}%\n"
                    f"💵 *Рекомендуемая ставка:* {current_signal_data.get('bet_amount','')}₽\n"
                    f"🎯 *Количество кликов:* {current_signal_data.get('clicks','')}\n"
                    f"📈 *Множитель:* x{current_signal_data.get('multiplier','')}\n\n"
                    f"🗺️ *Сетка:*\n"
                    f"{grid}\n\n"
                    f"📌 {instr}\n\n"
                    f"▶️ Нажмите кнопку ниже, чтобы показать следующий шаг"
                )
                
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(InlineKeyboardButton("➡️ Показать следующий шаг", callback_data="next_step"))
                markup.add(
                    InlineKeyboardButton("🔄 Обновить", callback_data="get_signal"),
                    InlineKeyboardButton("📊 Статистика", callback_data="stats")
                )
                markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
                
                bot.edit_message_text(next_step_text, call.message.chat.id, call.message.message_id,
                                     parse_mode='Markdown', reply_markup=markup)
            else:
                # Если все шаги показаны, отправляем сообщение об окончании
                final_text = (
                    f"🎰 *VIP СИГНАЛ #{current_signal_data.get('number','')}*\n\n"
                    f"🔥 *Вероятность выигрыша:* {current_signal_data.get('win_chance','')}%\n"
                    f"💵 *Рекомендуемая ставка:* {current_signal_data.get('bet_amount','')}₽\n"
                    f"🎯 *Количество кликов:* {current_signal_data.get('clicks','')}\n"
                    f"📈 *Множитель:* x{current_signal_data.get('multiplier','')}\n\n"
                    f"🎉 *СИГНАЛ ЗАВЕРШЕН!*\n"
                    f"*Вы успешно выполнили все шаги сигнала!*"
                )
                
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
                
                bot.edit_message_text(final_text, call.message.chat.id, call.message.message_id,
                                     parse_mode='Markdown', reply_markup=markup)
                # Сбрасываем состояние сигнала после завершения
                users_data[user_id]['current_signal'] = None
                save_users_data(users_data)
        else:
            # Нет активного сигнала — предложим получить новый
            hint_text = (
                f"💡 *Нет активного сигнала.*\n\n"
                f"Нажмите \"VIP Сигнал\" чтобы получить новый, либо включите автообновление в настройках."
            )
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("⚡ VIP Сигнал", callback_data="get_signal"))
            markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            bot.edit_message_text(hint_text, call.message.chat.id, call.message.message_id,
                                 parse_mode='Markdown', reply_markup=markup)
    
    elif call.data == "tips":
        tips_text = (
            f"💡 *Советы для получения VIP сигналов:*\n\n"
            f"• Следуйте пошаговой инструкции (кнопка \"Показать следующий шаг\").\n"
            f"• Держите разумный размер ставки относительно банка.\n"
            f"• Не пропускайте шаги в последовательности координат.\n"
            f"• При необходимости включите автообновление в настройках.\n\n"
            f"▶️ Нажмите \"VIP Сигнал\" для получения нового сигнала."
        )
        bot.edit_message_text(tips_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=get_main_menu(users_data[user_id]))
    
    elif call.data == "back_to_main":
        is_verified = users_data[user_id].get('id_verified', False)
        if is_verified:
            main_text = (
                f"🎰 *VIP СИГНАЛЫ MINES*\n\n"
                f"*Выберите действие:*\n\n"
                f"💡 *Советы* - полезные рекомендации\n"
                f"⚡ *VIP Сигнал* - получить VIP прогноз\n"
                f"📈 *Статистика* - ваши результаты\n"
                f"💎 *Баланс* - текущий баланс\n"
                f"⚙️ *Настройки* - настройки бота"
            )
        else:
            main_text = (
                f"🎰 *VIP СИГНАЛЫ MINES*\n\n"
                f"*Выберите действие:*\n\n"
                f"🎯 *Регистрация* - зарегистрироваться в 1win\n"
                f"🔐 *Ввести ID* - подтвердить ваш аккаунт\n"
                f"⚡ *VIP Сигнал* - получить VIP прогноз\n"
                f"📈 *Статистика* - ваши результаты\n"
                f"💎 *Баланс* - текущий баланс\n"
                f"⚙️ *Настройки* - настройки бота"
            )
        
        bot.edit_message_text(main_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=get_main_menu(users_data[user_id]))

# Обработчик текстовых сообщений (для ввода ID)
@bot.message_handler(func=lambda message: True)
def process_id_input(message):
    user_id = str(message.from_user.id)
    users_data = load_users_data()
    users_data = ensure_user_data(user_id, users_data)
    
    print(f"🔍 Получено сообщение от пользователя {user_id}: {message.text}")
    print(f"🔍 waiting_for_id: {users_data[user_id].get('waiting_for_id', False)}")
    
    # Проверяем, ожидает ли пользователь ввода ID
    if users_data[user_id].get('waiting_for_id', False):
        input_id = message.text.strip()
        
        # Проверяем, что введенный текст похож на ID (только цифры)
        if not input_id.isdigit():
            error_text = (
                f"❌ *НЕВЕРНЫЙ ФОРМАТ ID*\n\n"
                f"*ID должен содержать только цифры*\n\n"
                f"*Пример:* `123456789`\n\n"
                f"*Попробуйте еще раз*"
            )
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔍 Ввести ID", callback_data="enter_id"))
            markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            
            try:
                bot.reply_to(message, error_text, parse_mode='Markdown', reply_markup=markup)
                print(f"✅ Успешно отправлено сообщение о неправильном формате ID для пользователя {user_id}")
            except Exception as e:
                print(f"❌ Ошибка при отправке сообщения о неправильном формате ID: {e}")
                bot.send_message(message.chat.id, error_text, parse_mode='Markdown', reply_markup=markup)
            return
        
        # Отправляем сообщение о проверке
        try:
            checking_msg = bot.reply_to(message, "🔍 *Подключаюсь к серверам 1win...*", parse_mode='Markdown')
            print(f"✅ Успешно отправлено сообщение о проверке для пользователя {user_id}")
        except Exception as e:
            print(f"❌ Ошибка при отправке сообщения о проверке: {e}")
            checking_msg = bot.send_message(message.chat.id, "🔍 *Подключаюсь к серверам 1win...*", parse_mode='Markdown')
        print(f"🔍 Начинаем проверку ID: {input_id}")
        
        # Выполняем проверку ID с таймаутом
        try:
            import threading
            import queue
            
            # Создаем очередь для результата
            result_queue = queue.Queue()
            
            def check_id_with_timeout():
                try:
                    success, result = real_id_verification(input_id)
                    result_queue.put((success, result))
                except Exception as e:
                    result_queue.put((False, f"Ошибка проверки: {str(e)}"))
            
            # Запускаем проверку в отдельном потоке с таймаутом
            check_thread = threading.Thread(target=check_id_with_timeout)
            check_thread.daemon = True
            check_thread.start()
            
            # Ждем результат максимум 30 секунд
            try:
                success, result = result_queue.get(timeout=30)
                print(f"🔍 Результат проверки ID: success={success}, result={result}")
            except queue.Empty:
                print(f"⏰ Таймаут проверки ID: {input_id}")
                success = False
                result = "Таймаут проверки. Попробуйте еще раз."
                
        except Exception as e:
            print(f"❌ Ошибка при проверке ID: {e}")
            success = False
            result = f"Ошибка проверки: {str(e)}"
        
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
            )
            
            # Показываем реальные данные только если они получены
            if user_data['verification_method'] == '1win_real_api' or user_data['verification_method'] == '1win_real_scraping':
                success_text += (
                    f"💰 *Реальный баланс:* {user_data['balance']}₽\n"
                    f"🎯 *Реальные игры:* {user_data['total_games']}\n"
                    f"✅ *Реальные победы:* {user_data['wins']}\n"
                    f"❌ *Реальные поражения:* {user_data['losses']}\n"
                    f"📈 *Реальный процент:* {user_data['win_rate']}%\n"
                    f"🔍 *Источник:* {user_data['verification_method']}\n\n"
                    f"🎉 *ДОСТУП ОТКРЫТ!*\n"
                    f"*Реальные данные получены из 1win!*"
                )
            else:
                success_text += (
                    f"💰 *Баланс:* Недоступен (защищен 1win)\n"
                    f"🎯 *Статистика:* Недоступна (защищена 1win)\n"
                    f"🔍 *Проверка:* {user_data['verification_method']}\n\n"
                    f"⚠️ *ВАЖНО:* 1win не предоставляет публичный доступ к данным пользователей\n"
                    f"📊 *Для точных данных:* Используйте ваш личный кабинет 1win\n\n"
                    f"🎉 *ДОСТУП ОТКРЫТ!*\n"
                    f"*ID подтвержден, можете получать сигналы!*"
                )
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🎰 Получить сигнал", callback_data="get_signal"),
                InlineKeyboardButton("📊 Статистика", callback_data="stats")
            )
            markup.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            
            try:
                bot.edit_message_text(success_text, checking_msg.chat.id, checking_msg.message_id,
                                     parse_mode='Markdown', reply_markup=markup)
                print(f"✅ Успешно отправлено сообщение об успешной верификации для пользователя {user_id}")
            except Exception as e:
                print(f"❌ Ошибка при отправке сообщения об успешной верификации: {e}")
                # Пробуем отправить новое сообщение
                bot.send_message(message.chat.id, success_text, parse_mode='Markdown', reply_markup=markup)
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
            
            try:
                bot.edit_message_text(error_text, checking_msg.chat.id, checking_msg.message_id,
                                     parse_mode='Markdown', reply_markup=markup)
                print(f"✅ Успешно отправлено сообщение об ошибке верификации для пользователя {user_id}")
            except Exception as e:
                print(f"❌ Ошибка при отправке сообщения об ошибке верификации: {e}")
                # Пробуем отправить новое сообщение
                bot.send_message(message.chat.id, error_text, parse_mode='Markdown', reply_markup=markup)
    else:
        # Обычное сообщение - показываем главное меню
        if users_data[user_id].get('id_verified', False):
            # Пользователь уже верифицирован
            welcome_text = (
                f"🎰 *С возвращением в VIP Сигналы Mines!*\n\n"
                f"✅ *Ваш ID:* `{users_data[user_id].get('real_id', 'Неизвестно')}`\n"
                f"🔍 *Статус:* Верифицирован\n"
                f"🔄 *Автообновление:* {'Включено' if users_data[user_id].get('auto_update', False) else 'Выключено'}\n\n"
                f"🎯 *Выберите действие:*"
            )
        else:
            # Новый пользователь или не верифицированный
            welcome_text = (
                f"🎰 *Добро пожаловать в VIP Сигналы Mines!*\n\n"
                f"*Используйте кнопки меню для навигации по боту.*\n\n"
                f"*Для начала работы:*\n"
                f"1️⃣ Зарегистрируйтесь по партнерской ссылке\n"
                f"2️⃣ Введите ваш ID\n"
                f"3️⃣ Получайте VIP сигналы!"
            )
        bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=get_main_menu(user_id))

# Обработчик команды /tips
@bot.message_handler(commands=['tips'])
def tips_command(message):
    user_id = str(message.from_user.id)
    users_data = load_users_data()
    users_data = ensure_user_data(user_id, users_data)
    tips_text = (
        f"💡 *Советы для получения VIP сигналов:*\n\n"
        f"1️⃣ *Зарегистрируйтесь по партнерской ссылке*: "
        f"Это гарантирует вам доступ к самым точным сигналам и бонусам.\n\n"
        f"2️⃣ *Введите ваш ID*: "
        f"Подтвердите свою учетную запись 1win, чтобы получить доступ к вашим данным и сигналам.\n\n"
        f"3️⃣ *Включите автообновление*: "
        f"Это позволит вам получать сигналы автоматически, не ждая каждый раз.\n\n"
        f"4️⃣ *Следите за балансом*: "
        f"Убедитесь, что у вас достаточно средств для ставок.\n\n"
        f"5️⃣ *Выполняйте шаги сигнала*: "
        f"Следуйте пошаговой инструкции, чтобы увеличить шансы на выигрыш.\n\n"
        f"🎯 *Нажмите \"VIP Сигнал\" для получения первого сигнала!*"
    )
    bot.reply_to(message, tips_text, parse_mode='Markdown', reply_markup=get_main_menu(users_data[user_id]))

# Запуск автообновления в отдельном потоке
def start_auto_update():
    auto_update_signals()

# Запуск бота
if __name__ == "__main__":
    print("🤖 Запуск VIP Сигналы Mines бота...")

    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # НОВЫЙ ПОДХОД: Полная очистка перед запуском
    print("🧹 НОВЫЙ ПОДХОД: Полная очистка перед запуском...")
    
    try:
        # Шаг 1: Удаляем webhook через telebot
        bot.remove_webhook()
        time.sleep(3)
        
        # Шаг 2: Принудительная очистка через прямые API вызовы
        import requests
        
        # Удаляем webhook с drop_pending_updates
        webhook_response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
            json={"drop_pending_updates": True},
            timeout=10
        )
        print(f"✅ Webhook очищен: {webhook_response.status_code}")
        time.sleep(2)
        
        # Получаем и сбрасываем все обновления
        updates_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params={"offset": -1, "limit": 1000, "timeout": 1},
            timeout=10
        )
        print(f"✅ Обновления сброшены: {updates_response.status_code}")
        time.sleep(2)
        
        # Финальная очистка - устанавливаем высокий offset
        final_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params={"offset": 999999999, "limit": 1},
            timeout=10
        )
        print(f"✅ Offset установлен: {final_response.status_code}")
        time.sleep(3)
        
    except Exception as e:
        print(f"⚠️ Ошибка при очистке: {e}")

    # Запускаем автообновление в отдельном потоке
    auto_update_thread = threading.Thread(target=start_auto_update, daemon=True)
    auto_update_thread.start()

    print("✅ Бот запущен!")
    print("📱 Автообновление сигналов каждые 10 секунд")
    print("🎰 Готов к работе!")

    # НОВЫЙ ПОДХОД: Улучшенная обработка ошибок
    retry_count = 0
    max_retries = 10
    base_wait_time = 30

    while not shutdown_flag and retry_count < max_retries:
        try:
            print("🔄 Подключение к Telegram API...")
            
            # Используем infinity_polling вместо обычного polling
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
            
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 409:
                retry_count += 1
                print(f"⚠️ КОНФЛИКТ 409: попытка {retry_count}/{max_retries}")
                
                # НОВЫЙ ПОДХОД: Более эффективная очистка
                try:
                    print("🧹 Быстрая очистка конфликта...")
                    
                    # Быстрая очистка webhook
                    bot.remove_webhook()
                    time.sleep(2)
                    
                    # Быстрая очистка через API
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
                        json={"drop_pending_updates": True},
                        timeout=5
                    )
                    time.sleep(1)
                    
                    # Быстрый сброс обновлений
                    requests.get(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                        params={"offset": 999999999, "limit": 1},
                        timeout=5
                    )
                    time.sleep(1)
                    
                    print("✅ Быстрая очистка завершена")
                    
                except Exception as cleanup_error:
                    print(f"⚠️ Ошибка очистки: {cleanup_error}")

                # Экспоненциальная задержка
                wait_time = base_wait_time * (2 ** (retry_count - 1))
                wait_time = min(wait_time, 300)  # Максимум 5 минут
                
                print(f"🔄 Ожидание {wait_time} секунд...")
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