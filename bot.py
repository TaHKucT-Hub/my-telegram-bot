import os
import sqlite3
import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ============================================
# 1. ТОКЕН БОТА
# ============================================
TOKEN = "8952774961:AAE7jBZ2dpam5Tk45ZPnaNUmw3oRd-58LSI"

# ============================================
# 2. ID АДМИНИСТРАТОРА
# ============================================
ADMIN_ID = 123456789  # ЗАМЕНИ НА СВОЙ ID!

# ============================================
# 3. БАЗА ДАННЫХ
# ============================================
conn = sqlite3.connect("pushups.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    name TEXT,
    count INTEGER,
    date TEXT
)
""")
conn.commit()

# ============================================
# 4. БОТ
# ============================================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ============================================
# 5. ФРАЗЫ
# ============================================
MOTIVATION_PHRASES = [
    "💪 Ты машина! Так держать!",
    "🔥 Огонь! Ты лучший!",
    "🏆 Ты чемпион! Продолжай в том же духе!",
    "⚡ Ты неудержим! Ещё! Ещё!",
    "🎯 Точный удар! Ты на правильном пути!",
    "💯 Идеально! Ты превосходишь себя!",
    "🚀 Ты взлетаешь! Не останавливайся!",
    "👑 Ты король отжиманий!",
    "🎉 Супер! Ты вдохновляешь нас всех!",
    "😤 Ты зверь! Покажи всем, на что способен!",
    "🌟 Ты звезда! Сияй ярче!",
    "📈 Твой прогресс невероятен!",
    "🏋️ Ты настоящий атлет!",
    "💎 Ты алмаз! Оттачивай мастерство!",
    "🔥 Ты горишь! Продолжай жечь!",
]

GASLIGHT_PHRASES = [
    "😏 Саня, ты лох! Это всё, на что ты способен?",
    "🤣 Саня, ну ты и лох! Купил доску и не отжимаешься!",
    "😆 Саня, фуууу... лошара!",
    "😂 Саня, ты серьёзно? Это твой максимум?",
    "😜 Саня, даже бабушка больше отжимается!",
    "🤪 Саня, ты позорище!",
    "😏 Саня, слабо? А я думал, ты сильный...",
    "🤣 Саня, ты лох! Иди лучше доску продай!",
    "😆 Саня, ну ты и размазня!",
    "😂 Саня, ты меня смешишь!",
]

NOTIFICATION_PHRASES = [
    "📢 ВНИМАНИЕ! {name} отжался {count} раз!",
    "🔔 {name} сделал {count} отжиманий!",
    "💪 {name} накачал {count} раз!",
    "🏋️ {name} отжался {count}!",
    "🔥 {name} показал класс — {count} раз!",
    "📊 {name} добавил {count} отжиманий!",
]

# ============================================
# 6. ПРИВЕТСТВИЯ
# ============================================
HERO_GREETINGS = [
    "🏆 Дмитрий! Ты наш герой! Добро пожаловать в битву!\n\n📌 КОМАНДЫ:\n/allstats — статистика всех участников\n/top — таблица лидеров\n/mystats — моя статистика\n/today — результаты за сегодня\n/reset — сбросить мои результаты\n/getid — узнать свой ID",
    "💪 О, Дмитрий! Ты пришёл показать всем, как надо делать!\n\n📌 КОМАНДЫ:\n/allstats — статистика всех участников\n/top — таблица лидеров\n/mystats — моя статистика\n/today — результаты за сегодня",
    "🌟 Дмитрий! Ты звезда! Свети ярко!\n\n📌 КОМАНДЫ:\n/allstats — статистика всех участников\n/top — таблица лидеров\n/mystats — моя статистика\n/today — результаты за сегодня",
]

OTHER_GREETINGS = [
    "😏 Ну, Саня, ты лох! Пришёл посмотреть, как делают настоящие мужчины?\n\n📌 КОМАНДЫ:\n/allstats — статистика всех участников\n/top — таблица лидеров\n/mystats — моя статистика\n/today — результаты за сегодня\n/reset — сбросить мои результаты\n/getid — узнать свой ID",
    "🤣 Саня, ты реально думал, что у тебя получится?\n\n📌 КОМАНДЫ:\n/allstats — статистика всех участников\n/top — таблица лидеров\n/mystats — моя статистика\n/today — результаты за сегодня",
    "😆 О, Саня! Лошара в деле! Ну давай, удиви нас!\n\n📌 КОМАНДЫ:\n/allstats — статистика всех участников\n/top — таблица лидеров\n/mystats — моя статистика\n/today — результаты за сегодня",
]

# ============================================
# 7. КОМАНДА /getid
# ============================================
@dp.message(Command("getid"))
async def get_id(message: types.Message):
    await message.answer(
        f"📌 **Ваш ID:** `{message.from_user.id}`\n"
        f"👤 Имя: {message.from_user.first_name}\n"
        f"🔖 Username: @{message.from_user.username or 'нет'}",
        parse_mode="Markdown"
    )

# ============================================
# 8. КОМАНДА /start
# ============================================
@dp.message(Command("start"))
async def start(message: types.Message):
    username = message.from_user.username or ""
    if username == "Dmitriy_Tonkih":
        await message.answer(random.choice(HERO_GREETINGS))
    else:
        await message.answer(random.choice(OTHER_GREETINGS))

# ============================================
# 9. КОМАНДА /allstats
# ============================================
@dp.message(Command("allstats"))
async def all_stats(message: types.Message):
    cursor.execute("""
        SELECT name, SUM(count) as total, COUNT(DISTINCT date) as days
        FROM users GROUP BY user_id ORDER BY total DESC
    """)
    results = cursor.fetchall()

    if not results:
        await message.answer("📭 Пока никто не отжимался!")
        return

    total_all = sum(row[1] for row in results)
    msg = "📊 **ОБЩАЯ СТАТИСТИКА ВСЕХ УЧАСТНИКОВ** 📊\n\n"
    msg += f"👥 Всего участников: {len(results)}\n"
    msg += f"💪 Всего отжиманий: {total_all}\n\n"

    for i, (name, total, days) in enumerate(results, 1):
        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
        msg += f"{medal} {name} — {total} раз (за {days} дн.)\n"

    await message.answer(msg, parse_mode="Markdown")

# ============================================
# 10. КОМАНДА /top
# ============================================
@dp.message(Command("top"))
async def top(message: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT name, SUM(count) as total
        FROM users WHERE date = ? GROUP BY user_id ORDER BY total DESC LIMIT 10
    """, (today,))
    today_res = cursor.fetchall()

    cursor.execute("""
        SELECT name, SUM(count) as total
        FROM users WHERE date >= ? GROUP BY user_id ORDER BY total DESC LIMIT 10
    """, (week_ago,))
    week_res = cursor.fetchall()

    cursor.execute("""
        SELECT name, SUM(count) as total
        FROM users GROUP BY user_id ORDER BY total DESC LIMIT 10
    """)
    all_res = cursor.fetchall()

    msg = "🏆 **ТАБЛИЦА ЛИДЕРОВ** 🏆\n\n"

    msg += f"📅 **Сегодня** ({today}):\n"
    if today_res:
        for i, (name, total) in enumerate(today_res[:3], 1):
            m = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            msg += f"{m} {name} — {total}\n"
    else:
        msg += "📭 Сегодня никто не занимался\n"

    msg += f"\n📆 **За неделю**:\n"
    if week_res:
        for i, (name, total) in enumerate(week_res[:3], 1):
            m = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            msg += f"{m} {name} — {total}\n"
    else:
        msg += "📭 За неделю никто не занимался\n"

    msg += f"\n🏆 **За всё время**:\n"
    if all_res:
        for i, (name, total) in enumerate(all_res[:3], 1):
            m = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            msg += f"{m} {name} — {total}\n"
    else:
        msg += "📭 Пока никто не занимался\n"

    await message.answer(msg, parse_mode="Markdown")

# ============================================
# 11. КОМАНДА /mystats
# ============================================
@dp.message(Command("mystats"))
async def my_stats(message: types.Message):
    user_id = message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    cursor.execute("SELECT SUM(count) FROM users WHERE user_id = ? AND date = ?", (user_id, today))
    today_total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(count) FROM users WHERE user_id = ? AND date >= ?", (user_id, week_ago))
    week_total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(count) FROM users WHERE user_id = ?", (user_id,))
    all_total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(DISTINCT date) FROM users WHERE user_id = ?", (user_id,))
    days_count = cursor.fetchone()[0] or 0

    await message.answer(
        f"📊 **МОЯ СТАТИСТИКА**\n\n"
        f"📅 Сегодня: {today_total} отжиманий\n"
        f"📆 За неделю: {week_total} отжиманий\n"
        f"🏆 Всего: {all_total} отжиманий\n"
        f"📆 Активных дней: {days_count}"
    )

# ============================================
# 12. КОМАНДА /today
# ============================================
@dp.message(Command("today"))
async def today_stats(message: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT name, SUM(count) as total
        FROM users WHERE date = ? GROUP BY user_id ORDER BY total DESC
    """, (today,))
    results = cursor.fetchall()

    if not results:
        await message.answer("📭 Сегодня никто не отжимался!\n\nОтправь число, например 30 💪")
        return

    msg = f"📅 **РЕЗУЛЬТАТЫ ЗА СЕГОДНЯ** ({today})\n\n"
    for i, (name, total) in enumerate(results, 1):
        m = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
        msg += f"{m} {name} — {total} отжиманий\n"

    await message.answer(msg, parse_mode="Markdown")

# ============================================
# 13. КОМАНДА /reset
# ============================================
@dp.message(Command("reset"))
async def reset_stats(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    await message.answer("🔄 ВСЕ ТВОИ ОТЖИМАНИЯ СБРОШЕНЫ!")

# ============================================
# 14. ОБРАБОТКА ЧИСЕЛ (ТОЛЬКО ЕСЛИ НЕ КОМАНДА)
# ============================================
@dp.message()
async def handle_numbers(message: types.Message):
    # Проверяем, что сообщение — это число
    try:
        count = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Я понимаю только числа!\n\n"
            "Пример: 30  → добавить 30\n"
            "Пример: 17 13 15  → 17+13+15 = 45\n\n"
            "📌 КОМАНДЫ:\n"
            "/allstats — статистика всех участников\n"
            "/top — таблица лидеров\n"
            "/mystats — моя статистика\n"
            "/today — результаты за сегодня\n"
            "/reset — сбросить мои результаты\n"
            "/getid — узнать свой ID"
        )
        return

    if count <= 0:
        await message.answer("❌ Число должно быть больше 0!")
        return
    if count > 1000:
        await message.answer("😱 Слишком много! Максимум 1000.")
        return

    user_id = message.from_user.id
    username = message.from_user.username or ""
    name = message.from_user.first_name
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO users (user_id, username, name, count, date) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, name, count, today)
    )
    conn.commit()

    cursor.execute(
        "SELECT SUM(count) FROM users WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    today_total = cursor.fetchone()[0] or 0

    if username == "Dmitriy_Tonkih":
        phrase = random.choice(MOTIVATION_PHRASES)
    else:
        phrase = random.choice(GASLIGHT_PHRASES)

    await message.answer(
        f"✅ +{count} ОТЖИМАНИЙ!\n"
        f"{phrase}\n"
        f"📅 СЕГОДНЯ: {today_total} ОТЖИМАНИЙ"
    )

    # Уведомление администратору
    try:
        await bot.send_message(
            ADMIN_ID,
            random.choice(NOTIFICATION_PHRASES).format(name=name, count=count)
        )
    except:
        pass

# ============================================
# 15. ЗАПУСК БОТА
# ============================================
async def main():
    print("🚀 БОТ ЗАПУЩЕН!")
    print("📱 ОТПРАВЛЯЙ ЧИСЛА: 30 ИЛИ 17 13 15")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())