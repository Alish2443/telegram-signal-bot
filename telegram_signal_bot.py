import os
import sys
import time
import json
import random
import signal
import threading
import re
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

# ========= Конфиг =========
BOT_TOKEN = (os.environ.get("BOT_TOKEN") or "").strip()
PARTNER_LINK = os.environ.get("PARTNER_LINK", "https://example.com")  # замени на свою партнёрскую ссылку
USERS_FILE = os.environ.get("USERS_FILE", "/app/data/users_data.json")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN не задан.")
    sys.exit(1)

# MSK time
try:
    from zoneinfo import ZoneInfo
    def get_msk_time_str():
        return datetime.now(ZoneInfo("Europe/Moscow")).strftime("%H:%M:%S")
except Exception:
    def get_msk_time_str():
        # Fallback UTC+3
        return time.strftime("%H:%M:%S", time.gmtime(time.time() + 3 * 3600))

bot = telebot.TeleBot(BOT_TOKEN)
shutdown_flag = False

# ========= Безопасное редактирование =========
def safe_edit_message_text(text, chat_id, message_id, reply_markup=None, parse_mode='Markdown'):
    try:
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode=parse_mode, reply_markup=reply_markup
        )
    except ApiTelegramException as e:
        if e.error_code == 400 and 'message is not modified' in str(e):
            return
        raise

# ========= Пользовательские данные =========
def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def load_users_data():
    try:
        _ensure_dir(USERS_FILE)
        if not os.path.exists(USERS_FILE):
            print(f"📁 Файл данных не найден, создаем новый: {USERS_FILE}")
            return {}
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"⚠️ Ошибка загрузки данных: {e}")
        return {}

def save_users_data(data: dict):
    try:
        _ensure_dir(USERS_FILE)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения данных: {e}")

def init_user(user_id: str) -> dict:
    return {
        "auto_update": False,
        "last_signal_time": 0.0,
        "current_signal": None,
        "stats": {"wins": 0, "losses": 0, "balance": 0}
    }

def ensure_user_data(user_id: str, data: dict) -> dict:
    if user_id not in data:
        data[user_id] = init_user(user_id)
        save_users_data(data)
    return data

# ========= Главное меню =========
def get_main_menu():
    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(
        InlineKeyboardButton("💡 Советы", callback_data="tips_page_1"),
        InlineKeyboardButton("📈 Статистика", callback_data="stats")
    )
    mk.add(
        InlineKeyboardButton("⚡ VIP Сигнал", callback_data="get_signal"),
        InlineKeyboardButton("💎 Баланс", callback_data="balance")
    )
    mk.add(InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
    return mk

# ========= Генерация сигнала + сетка =========
LETTERS = ["A", "B", "C", "D", "E"]
NUMBERS = ["1", "2", "3", "4", "5"]

def generate_signal():
    win_chance = random.choice([85, 87, 89, 91, 93, 95, 97])
    bet_amount = random.choice([100, 150, 200, 250, 300, 400, 500, 750, 1000])
    clicks = random.choice([2, 3, 4, 5])
    if clicks == 2:
        multiplier = round(random.uniform(1.8, 2.5), 2)
    elif clicks == 3:
        multiplier = round(random.uniform(2.2, 3.2), 2)
    elif clicks == 4:
        multiplier = round(random.uniform(2.8, 4.0), 2)
    else:
        multiplier = round(random.uniform(3.5, 5.0), 2)
    return {"win_chance": win_chance, "bet_amount": bet_amount, "clicks": clicks, "multiplier": multiplier}

def generate_coords_sequence(steps_count: int):
    cells = [f"{l}{n}" for l in LETTERS for n in NUMBERS]
    random.shuffle(cells)
    return cells[:steps_count]

def render_grid_with_labels():
    header = "    " + "  ".join(NUMBERS)
    rows = [f"{letter} | ⬛ ⬛ ⬛ ⬛ ⬛" for letter in LETTERS]
    return "\n".join([header] + rows)

def format_instruction(coords: list, revealed: int):
    total = len(coords)
    if total == 0:
        return ""
    if revealed <= 0:
        preview = f"{coords[0]} → …"
    elif revealed >= total:
        preview = " → ".join(coords)
    else:
        preview = " → ".join(coords[:revealed]) + " → …"
    return f"Нажимай по порядку: {preview}\n(открыто {revealed} из {total})"

# ========= Советы (3 страницы) =========
# TODO: Вставь свой законный контент (ниже — заглушки)

DISCLAIMER = (
    "⚠️ Отказ от ответственности:\n"
    "Материал носит информационный характер, не является призывом к действию.\n\n"
)

TIPS_PAGES = [
    (
        "💡 Совет 1 — Заголовок",
        DISCLAIMER +
        "💸 АБУЗ 1WIN — 8–15К С КРУГА БЕЗ ВЛОЖЕНИЙ
@abyzimtyt1win | 🔥 Актуально: АВГУСТ 2025 • 8 августа в 1:15
Задолбался жить на дошиках, пахать за копейки или у мамы на шее?

 Пока ты думаешь, другие лутают деньги без опыта и без бюджета на рекламу.

⚠️ Вот схема, которая прямо сейчас приносит от 10К до 30К с круга.

 Промокод: AVATWIN

⚙️ ЧТО ДЕЛАТЬ:
Переходишь по ссылке (офиц. сайт 1WIN):
 👉 НАЖМИ СЮДА ДЛЯ РЕГИСТРАЦИИ
Регаешь новый акк
 Обязательно жмёшь “Добавить промокод” и вводишь:
 🔑 AVATWIN
✅ За это получаешь:

 • +500% к первому депозиту (до 4 раз)

 • 70 фриспинов в слоты



💰 ТЕПЕРЬ ПРО БАБКИ:
Пополняешь баланс от 1.500 ₽ до 100.000 ₽
 👉 Чем больше — тем жирнее откат с фриспинов.
🧠 Примеры:

 • Залил 2.000 ₽ — снял 13.800 ₽

 • Друг закинул 10К — вывел 47.000 ₽

 📈 ROI с круга: от x2 до x5



🎰 КУДА КРУТИТЬ:
Заходишь в слот:
 → Aviator
 → Book of Ra
Крутишь все 70 фриспинов → забираешь профит → выводишь 💸

📤 Без паспорта. Моментальный вывод — хоть на карту, хоть на киви, хоть в крипту.



🧯 А ЕСЛИ ПРОЕБАЛ?
🟢 Спокойно. У 1WIN есть кэшбэк до 30% от проигранных за неделю.

 Т.е. даже если всё слил — можешь получить часть бабок обратно.

 И снова попробовать.

🔁 Каждую неделю система возвращает % от минусов.

 🧾 Ничего не надо заполнять, всё начисляется автоматом.

📌 ИТОГ:
• Промо: AVATWIN

 • Бонус: +500% и 70 фриспинов

 • Профит: до 30К за круг

 • Даже если слил — получаешь назад до 30% кэшбэка

👉 Залетай по ссылке и начни лутать

 Пока халява работает — юзай. Потом порежут.
        .\n\n"
        f"Контакт: @abyzimtyt1win\nСсылка: {PARTNER_LINK}"
    ),
    (
        "💡 Совет 2 — Заголовок",
        DISCLAIMER +
        "💣 1WIN — СКРЫТЫЙ МЕХАНИЗМ CASHBACK 300%
📅 Актуально: Август 2025
📍 GEO: РФ / СНГ

⚠️ Нашёл косяк в акциях 1WIN: при активации кешбэка и быстрой смене валюты аккаунта система начисляет тройной возврат от проигрышей.
Проверено на 4 акках — реально капает X3 к слитым ставкам.

📌 Как делать:
1️⃣ Создаёшь новый акк по ссылке → [ссылка]
2️⃣ В настройках сразу ставишь валюту USD.
3️⃣ Активируешь «Кешбэк до 30%».
4️⃣ Ставишь на высокие коэффициенты в LIVE (от 5.0).
5️⃣ После проигрыша моментально меняешь валюту на RUB и обратно.

💰 Результат:
— Система видит проигрыш как «мультивалютный» и возвращает ×3 кешбэк.

📤 Вывод без проблем, до 50k в день.

🚨 Дырка живёт максимум неделю.

🔥 1WIN — ДВОЙНОЙ БОНУС ЗА ДЕПОЗИТ
📅 Актуально: Август 2025
📍 GEO: РФ / СНГ

⚠️ Нашёл баг в пополнениях: при использовании крипты и карты подряд бонус за депозит начисляется дважды.
Проверил — работает на любом новом акке.

📌 Как делать:
1️⃣ Регаешь свежий акк по ссылке → [ссылка]
2️⃣ Пополняешь на 500₽ картой → активируешь бонус за депозит.
3️⃣ Сразу пополняешь ещё на 500₽ через крипту (USDT/BTC).
4️⃣ Получаешь бонус от первой и второй суммы отдельно.

💰 Результат:
— На счёт падает ×2 бонусных денег, которые можно проставить и вывести.

📤 Вывод без верификации, на любую карту или крипту.

🚨 Живёт недолго, фиксится быстро.
 №2.\n\n"
        f"Контакт: @abyzimtyt1win\nСсылка: {PARTNER_LINK}"
    ),
    (
        "💡 Совет 3 — Заголовок",
        DISCLAIMER +
        "💣 НОВАЯ ЛАЗЕЙКА 1WIN — ДЕНЬГИ ПАДАЮТ САМИ
📅 Актуально: Август 2025
📍 GEO: РФ / СНГ

⚠️ Нашёл баг в live-ставках 1WIN: система возвращает проигранную ставку, если после неё быстро сделать вторую на тот же матч.
Работает пока не пофиксили (проверено на 6 аккаунтах).

📌 Как делать:

Регаешь новый акк по ссылке → [ссылка]

Пополняешь от 500₽ (меньше — не срабатывает).

Заходишь в LIVE-ставки, выбираешь матч, где идёт 2-й тайм.

Ставишь на проигрывающую сторону (чтобы коэффициент был от 3).

После того как ставка улетела, сразу повторяешь её второй раз на ту же команду с той же суммой.

💰 Результат:
— Первая ставка может слиться,
— Вторая возвращается как выигрыш, даже если команда всё равно проиграла (система дублирует возврат).

📤 Вывод моментально, без верификации.

🚨 Держится максимум неделю, потом пофиксят. Успей зайти, пока дыра живая.


💥 1WIN — «ЗАСТРЯВШАЯ» СТАВКА = Х2 БАЛАНС
📅 Актуально: Август 2025
📍 GEO: РФ / СНГ

⚠️ Поймал баг в обработке ставок: если поставить в LIVE и сразу отменить через поддержку, баланс удваивается.
Работает только на свежих аккаунтах!

📌 Как делать:
1️⃣ Регаешь новый акк по ссылке → [ссылка]
2️⃣ Заходишь в LIVE-ставки и ставишь минимум 1000₽.
3️⃣ Мгновенно пишешь в чат поддержки: «Ставка зависла, отмените».
4️⃣ Через пару минут баланс возвращают, но ставка остаётся активной.

💰 Результат:
— Если ставка выигрывает — получаешь и возврат, и выигрыш.

📤 Вывод до 30k без доков.

🚨 Проверено на 3 акках, живёт пару дней.

 №3.\n\n"
        f"Контакт: @abyzimtyt1win\nСсылка: {PARTNER_LINK}"
    ),
]


def render_tips_page(page_index: int):
    total = len(TIPS_PAGES)
    page_index = max(0, min(total - 1, page_index))
    title, body = TIPS_PAGES[page_index]
    header = f"{title}\n\nСтр. {page_index + 1}/{total}\n\n"
    text = header + body

    mk = InlineKeyboardMarkup(row_width=3)
    btns = []
    if page_index > 0:
        btns.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"tips_page_{page_index}"))
    btns.append(InlineKeyboardButton(f"{page_index + 1}/{total}", callback_data=f"tips_page_{page_index + 1}"))
    if page_index < total - 1:
        btns.append(InlineKeyboardButton("➡️ Далее", callback_data=f"tips_page_{page_index + 2}"))
    if btns:
        mk.add(*btns)
    mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
    return text, mk

# ========= Автообновление =========
def auto_update_signals():
    while not shutdown_flag:
        time.sleep(10)
        users = load_users_data()
        for uid, udata in users.items():
            if udata.get("auto_update"):
                try:
                    now = time.time()
                    if now - udata.get("last_signal_time", 0) < 10:
                        continue
                    sig = generate_signal()
                    number = random.randint(1000, 9999)
                    coords = generate_coords_sequence(sig["clicks"])
                    users[uid]["current_signal"] = {
                        "number": number,
                        "coords": coords,
                        "revealed": 0,
                        "created_at": now,
                        "win_chance": sig["win_chance"],
                        "bet_amount": sig["bet_amount"],
                        "clicks": sig["clicks"],
                        "multiplier": sig["multiplier"]
                    }
                    users[uid]["last_signal_time"] = now
                    save_users_data(users)

                    grid = render_grid_with_labels()
                    instr = format_instruction(coords, 0)
                    text = (
                        f"🔄 *АВТООБНОВЛЕНИЕ СИГНАЛА*\n\n"
                        f"🎰 *VIP СИГНАЛ #{number}*\n\n"
                        f"🔥 Вероятность выигрыша: *{sig['win_chance']}%*\n"
                        f"💵 Рекомендуемая ставка: *{sig['bet_amount']}₽*\n"
                        f"🎯 Количество кликов: *{sig['clicks']}*\n"
                        f"📈 Множитель: *x{sig['multiplier']}*\n\n"
                        f"🗺️ *Сетка:*\n{grid}\n\n"
                        f"📌 {instr}\n\n"
                        f"🕐 Время (МСК): *{get_msk_time_str()}*"
                    )
                    mk = InlineKeyboardMarkup(row_width=2)
                    mk.add(InlineKeyboardButton("➡️ Показать следующий шаг", callback_data="next_step"))
                    mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
                    bot.send_message(int(uid), text, parse_mode='Markdown', reply_markup=mk)
                except Exception as e:
                    print(f"⚠️ Ошибка автообновления для {uid}: {e}")

# ========= Команды =========
@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = str(message.from_user.id)
    data = ensure_user_data(user_id, load_users_data())
    welcome = (
        "🎰 *VIP СИГНАЛЫ MINES*\n\n"
        "*Выберите действие:*"
    )
    bot.reply_to(message, welcome, parse_mode='Markdown', reply_markup=get_main_menu())

@bot.message_handler(commands=["status"])
def status_command(message):
    user_id = str(message.from_user.id)
    data = ensure_user_data(user_id, load_users_data())
    st = data[user_id]["stats"]
    text = (
        "📊 *СТАТУС*\n\n"
        f"💰 Баланс: {st.get('balance',0)}₽\n"
        f"✅ Победы: {st.get('wins',0)}\n"
        f"❌ Поражения: {st.get('losses',0)}"
    )
    bot.reply_to(message, text, parse_mode='Markdown', reply_markup=get_main_menu())

# ========= Callback =========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    data = ensure_user_data(user_id, load_users_data())

    # Советы: первая страница
    if call.data == "tips_page_1":
        text, mk = render_tips_page(0)
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        return

    # Советы: навигация tips_page_N
    if call.data.startswith("tips_page_"):
        try:
            idx = int(call.data.split("_")[-1]) - 1
        except:
            idx = 0
        text, mk = render_tips_page(idx)
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        return

    if call.data == "back_to_main":
        main_text = (
            "🎰 *VIP СИГНАЛЫ MINES*\n\n"
            "*Выберите действие:*"
        )
        safe_edit_message_text(main_text, call.message.chat.id, call.message.message_id,
                               reply_markup=get_main_menu())
        return

    if call.data == "settings":
        auto_status = "🟢 ВКЛ" if data[user_id].get("auto_update") else "🔴 ВЫКЛ"
        text = (
            "⚙️ *Настройки*\n\n"
            f"🔄 Автообновление: {auto_status}\n\n"
            "Выберите режим:"
        )
        mk = InlineKeyboardMarkup(row_width=2)
        if data[user_id].get("auto_update"):
            mk.add(InlineKeyboardButton("🔴 Отключить авто", callback_data="disable_auto"))
        else:
            mk.add(InlineKeyboardButton("🟢 Включить авто", callback_data="enable_auto"))
        mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        return

    if call.data == "enable_auto":
        data[user_id]["auto_update"] = True
        save_users_data(data)
        text = "✅ *АВТООБНОВЛЕНИЕ ВКЛЮЧЕНО*\n\nТеперь сигналы будут приходить автоматически."
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id,
                               reply_markup=get_main_menu())
        return

    if call.data == "disable_auto":
        data[user_id]["auto_update"] = False
        save_users_data(data)
        text = "❌ *АВТООБНОВЛЕНИЕ ОТКЛЮЧЕНО*\n\nПолучайте сигналы вручную."
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id,
                               reply_markup=get_main_menu())
        return

    if call.data == "stats":
        st = data[user_id]["stats"]
        text = (
            "📊 *СТАТИСТИКА*\n\n"
            f"💰 Баланс: {st.get('balance',0)}₽\n"
            f"✅ Победы: {st.get('wins',0)}\n"
            f"❌ Поражения: {st.get('losses',0)}"
        )
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        return

    if call.data == "balance":
        st = data[user_id]["stats"]
        text = (
            "💰 *БАЛАНС*\n\n"
            f"Текущий баланс: {st.get('balance',0)}₽\n"
            f"📊 Обновлено (МСК): {get_msk_time_str()}"
        )
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        return

    if call.data == "get_signal":
        now = time.time()
        if now - data[user_id].get("last_signal_time", 0) < 10:
            cooldown = 10 - int(now - data[user_id].get("last_signal_time", 0))
            text = (
                "⏰ *ПЕРЕЗАРЯДКА АКТИВНА*\n\n"
                f"🔄 Осталось: {cooldown} сек\n"
                "💡 Подождите немного перед следующим запросом"
            )
            mk = InlineKeyboardMarkup(row_width=2)
            mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
            return

        sig = generate_signal()
        number = random.randint(1000, 9999)
        coords = generate_coords_sequence(sig["clicks"])
        data[user_id]["current_signal"] = {
            "number": number,
            "coords": coords,
            "revealed": 0,
            "created_at": now,
            "win_chance": sig["win_chance"],
            "bet_amount": sig["bet_amount"],
            "clicks": sig["clicks"],
            "multiplier": sig["multiplier"]
        }
        data[user_id]["last_signal_time"] = now
        save_users_data(data)

        grid = render_grid_with_labels()
        instr = format_instruction(coords, 0)
        text = (
            f"🎰 *VIP СИГНАЛ #{number}*\n\n"
            f"🔥 Вероятность выигрыша: {sig['win_chance']}%\n"
            f"💵 Рекомендуемая ставка: {sig['bet_amount']}₽\n"
            f"🎯 Количество кликов: {sig['clicks']}\n"
            f"📈 Множитель: x{sig['multiplier']}\n\n"
            f"🗺️ *Сетка:*\n{grid}\n\n"
            f"📌 {instr}\n\n"
            f"▶️ Нажмите кнопку ниже, чтобы показать следующий шаг"
        )
        mk = InlineKeyboardMarkup(row_width=2)
        mk.add(InlineKeyboardButton("➡️ Показать следующий шаг", callback_data="next_step"))
        mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        return

    if call.data == "next_step":
        cur = data[user_id].get("current_signal")
        if not cur or not isinstance(cur, dict) or not cur.get("coords"):
            text = "💡 *Нет активного сигнала.*\nНажмите «VIP Сигнал»."
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("⚡ VIP Сигнал", callback_data="get_signal"))
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
            return

        revealed = cur["revealed"]
        total = len(cur["coords"])
        if revealed < total:
            revealed += 1
            cur["revealed"] = revealed
            data[user_id]["current_signal"] = cur
            save_users_data(data)

            grid = render_grid_with_labels()
            instr = format_instruction(cur["coords"][:revealed], revealed)
            text = (
                f"🎰 *VIP СИГНАЛ #{cur.get('number','')}*\n\n"
                f"🔥 Вероятность выигрыша: {cur.get('win_chance','')}%\n"
                f"💵 Рекомендуемая ставка: {cur.get('bet_amount','')}₽\n"
                f"🎯 Количество кликов: {cur.get('clicks','')}\n"
                f"📈 Множитель: x{cur.get('multiplier','')}\n\n"
                f"🗺️ *Сетка:*\n{grid}\n\n"
                f"📌 {instr}\n\n"
                f"▶️ Нажмите кнопку ниже, чтобы показать следующий шаг"
            )
            mk = InlineKeyboardMarkup(row_width=2)
            if revealed < total:
                mk.add(InlineKeyboardButton("➡️ Показать следующий шаг", callback_data="next_step"))
            mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
            return

        # завершено
        text = (
            f"🎰 *VIP СИГНАЛ #{cur.get('number','')}*\n\n"
            "🎉 *СИГНАЛ ЗАВЕРШЕН!*"
        )
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        data[user_id]["current_signal"] = None
        save_users_data(data)
        return

# ========= Сигналы завершения =========
def signal_handler(signum, frame):
    global shutdown_flag
    print("\n🛑 Завершение…")
    shutdown_flag = True
    try:
        bot.stop_polling()
    except:
        pass
    sys.exit(0)

# ========= Запуск =========
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Предполетная проверка токена
    try:
        me = bot.get_me()
        print(f"🤖 Бот: @{me.username} (id={me.id})")
    except ApiTelegramException as e:
        if e.error_code == 401:
            print("❌ Неверный BOT_TOKEN (401).")
            sys.exit(1)
        raise

    th = threading.Thread(target=auto_update_signals, daemon=True)
    th.start()

    print("✅ Бот запущен. Поллинг…")
    bot.infinity_polling(timeout=60, long_polling_timeout=60) 
