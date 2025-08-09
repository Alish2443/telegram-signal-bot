import os
import sys
import time
import json
import random
import signal
import threading
import traceback
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

# ========= Конфиг =========
BOT_TOKEN = (os.environ.get("BOT_TOKEN") or "").strip()
PARTNER_LINK = os.environ.get("PARTNER_LINK", "https://example.com")
USERS_FILE = os.environ.get("USERS_FILE", "/app/data/users_data.json")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN не задан.")
    sys.exit(1)

# ========= Время (MSK) =========
try:
    from zoneinfo import ZoneInfo
    def get_msk_time_str():
        return datetime.now(ZoneInfo("Europe/Moscow")).strftime("%H:%M:%S")
except Exception:
    def get_msk_time_str():
        # fallback UTC+3
        return time.strftime("%H:%M:%S", time.gmtime(time.time() + 3 * 3600))

# ========= Телеграм бот =========
bot = telebot.TeleBot(BOT_TOKEN)
shutdown_flag = False

# ========= Блокировка файловой записи =========
_users_file_lock = threading.Lock()

# ========= Вспомогательные функции для файлов/директорий =========
def _ensure_dir(path: str):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def load_users_data():
    try:
        _ensure_dir(USERS_FILE)
        if not os.path.exists(USERS_FILE):
            print(f"📁 Файл данных не найден, создаем новый: {USERS_FILE}")
            return {}
        with _users_file_lock:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f) or {}
                except json.JSONDecodeError:
                    print("⚠️ JSONDecodeError: файл данных повреждён или пуст — возвращаю пустой словарь.")
                    return {}
    except Exception as e:
        print(f"⚠️ Ошибка загрузки данных: {e}")
        traceback.print_exc()
        return {}

def save_users_data(data: dict):
    try:
        _ensure_dir(USERS_FILE)
        with _users_file_lock:
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения данных: {e}")
        traceback.print_exc()

# ========= User data helpers =========
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

# ========= UI: главное меню =========
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

# ========= Сигналы и сетка =========
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

# ========= Советы (заглушки) =========
DISCLAIMER = (
    "⚠️ Отказ от ответственности:\n"
    "Материал носит информационный характер, не является призывом к действию.\n\n"
)

# NOTE: оставил тексты твоих советов как есть, только ссылка подставляется
TIPS_PAGES = [
    (
        "💡 Совет 1 — Заголовок",
        DISCLAIMER + f"... (контент) ...\n\nКонтакт: @abyzimtyt1win\nСсылка: {PARTNER_LINK}"
    ),
    (
        "💡 Совет 2 — Заголовок",
        DISCLAIMER + f"... (контент) ...\n\nКонтакт: @abyzimtyt1win\nСсылка: {PARTNER_LINK}"
    ),
    (
        "💡 Совет 3 — Заголовок",
        DISCLAIMER + f"... (контент) ...\n\nКонтакт: @abyzimtyt1win\nСсылка: {PARTNER_LINK}"
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
    # средняя кнопка — неактивный лейбл, сделал noop
    btns.append(InlineKeyboardButton(f"{page_index + 1}/{total}", callback_data="noop"))
    if page_index < total - 1:
        btns.append(InlineKeyboardButton("➡️ Далее", callback_data=f"tips_page_{page_index + 2}"))
    if btns:
        mk.add(*btns)
    mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
    return text, mk

# ========= safe edit message =========
def safe_edit_message_text(text, chat_id, message_id, reply_markup=None, parse_mode='Markdown'):
    try:
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode=parse_mode, reply_markup=reply_markup
        )
    except ApiTelegramException as e:
        try:
            err_str = str(e).lower()
            if 'message is not modified' in err_str or 'not modified' in err_str:
                return
            # иногда есть description
            if 'description' in dir(e) and e.description and 'not modified' in str(e.description).lower():
                return
        except Exception:
            pass
        # если не распознали — печатаем трейс и пробрасываем ошибку выше
        print("⚠️ ApiTelegramException в safe_edit_message_text:")
        traceback.print_exc()
        raise

# ========= Автообновление (в отдельном потоке) =========
def auto_update_signals():
    while not shutdown_flag:
        time.sleep(10)
        try:
            users = load_users_data()
            for uid, udata in list(users.items()):
                try:
                    if udata.get("auto_update"):
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
                        try:
                            bot.send_message(int(uid), text, parse_mode='Markdown', reply_markup=mk)
                        except Exception:
                            # не падаем весь поток из-за одного юзера
                            print(f"⚠️ Не удалось отправить автообновление пользователю {uid}")
                            traceback.print_exc()
                except Exception:
                    print(f"⚠️ Ошибка внутри цикла автообновления для {uid}:")
                    traceback.print_exc()
        except Exception:
            print("⚠️ Ошибка в auto_update_signals (внешняя):")
            traceback.print_exc()

# ========= Команды =========
@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = str(message.from_user.id)
    data = load_users_data()
    ensure_user_data(user_id, data)
    welcome = (
        "🎰 *VIP СИГНАЛЫ MINES*\n\n"
        "*Выберите действие:*"
    )
    bot.reply_to(message, welcome, parse_mode='Markdown', reply_markup=get_main_menu())

@bot.message_handler(commands=["status"])
def status_command(message):
    user_id = str(message.from_user.id)
    data = load_users_data()
    ensure_user_data(user_id, data)
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
    data = load_users_data()
    ensure_user_data(user_id, data)

    # noop
    if call.data == "noop":
        # просто игнорируем нажатие средней кнопки
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass
        return

    # Советы: первая страница
    if call.data == "tips_page_1":
        try:
            text, mk = render_tips_page(0)
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        except Exception:
            traceback.print_exc()
        return

    # Навигация tips_page_N
    if call.data.startswith("tips_page_"):
        try:
            idx = int(call.data.split("_")[-1]) - 1
        except Exception:
            idx = 0
        try:
            text, mk = render_tips_page(idx)
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        except Exception:
            traceback.print_exc()
        return

    if call.data == "back_to_main":
        main_text = (
            "🎰 *VIP СИГНАЛЫ MINES*\n\n"
            "*Выберите действие:*"
        )
        try:
            safe_edit_message_text(main_text, call.message.chat.id, call.message.message_id,
                                   reply_markup=get_main_menu())
        except Exception:
            traceback.print_exc()
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
        try:
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        except Exception:
            traceback.print_exc()
        return

    if call.data == "enable_auto":
        data[user_id]["auto_update"] = True
        save_users_data(data)
        text = "✅ *АВТООБНОВЛЕНИЕ ВКЛЮЧЕНО*\n\nТеперь сигналы будут приходить автоматически."
        try:
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id,
                                   reply_markup=get_main_menu())
        except Exception:
            traceback.print_exc()
        return

    if call.data == "disable_auto":
        data[user_id]["auto_update"] = False
        save_users_data(data)
        text = "❌ *АВТООБНОВЛЕНИЕ ОТКЛЮЧЕНО*\n\nПолучайте сигналы вручную."
        try:
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id,
                                   reply_markup=get_main_menu())
        except Exception:
            traceback.print_exc()
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
        try:
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        except Exception:
            traceback.print_exc()
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
        try:
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        except Exception:
            traceback.print_exc()
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
            try:
                safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
            except Exception:
                traceback.print_exc()
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
        try:
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
        except Exception:
            traceback.print_exc()
        return

    if call.data == "next_step":
        cur = data[user_id].get("current_signal")
        if not cur or not isinstance(cur, dict) or not cur.get("coords"):
            text = "💡 *Нет активного сигнала.*\nНажмите «VIP Сигнал»."
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("⚡ VIP Сигнал", callback_data="get_signal"))
            try:
                safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
            except Exception:
                traceback.print_exc()
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
            try:
                safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
            except Exception:
                traceback.print_exc()
            return

        # завершено
        text = (
            f"🎰 *VIP СИГНАЛ #{cur.get('number','')}*\n\n"
            "🎉 *СИГНАЛ ЗАВЕРШЕН!*"
        )
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
        try:
            safe_edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)
            data[user_id]["current_signal"] = None
            save_users_data(data)
        except Exception:
            traceback.print_exc()
        return

# ========= Завершение процесса =========
def signal_handler(signum, frame):
    global shutdown_flag
    print("\n🛑 Завершение…")
    shutdown_flag = True
    try:
        bot.stop_polling()
    except Exception:
        pass
    sys.exit(0)

# ========= Запуск =========
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        me = bot.get_me()
        print(f"🤖 Бот: @{me.username} (id={me.id})")
    except ApiTelegramException as e:
        if getattr(e, "error_code", None) == 401:
            print("❌ Неверный BOT_TOKEN (401).")
            sys.exit(1)
        print("⚠️ ApiTelegramException при get_me():")
        traceback.print_exc()
        sys.exit(1)
    except Exception:
        print("⚠️ Ошибка при инициализации бота:")
        traceback.print_exc()
        sys.exit(1)

    th = threading.Thread(target=auto_update_signals, daemon=True)
    th.start()

    print("✅ Бот запущен. Поллинг…")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
