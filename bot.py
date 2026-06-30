import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime, timedelta
import random

# ============================================
# 1. ТОКЕН БОТА (вставь свой!)
# ============================================
TOKEN = "8952774961:AAE7jBZ2dpam5Tk45ZPnaNUmw3oRd-58LSI"

# ============================================
# 2. ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ
# ============================================
WELCOME_TEXT = """💪 ПРИВЕТ! ЭТО БОТ ДЛЯ ОТЖИМАНИЙ!

Просто отправь мне ЧИСЛО:
30  →  добавлю 30 отжиманий
17 13 15  →  сложу все = 45 отжиманий

📌 КОМАНДЫ:
/top  — таблица лидеров
/mystats  — моя статистика
/today  — результаты за сегодня
/reset  — сбросить мои результаты

🏆 СОРЕВНУЙСЯ С ДРУЗЬЯМИ!"""

# ============================================
# 3. ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ
# ============================================
conn = sqlite3.connect("pushups.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    count INTEGER,
    date TEXT
)
""")
conn.commit()

# ============================================
# 4. СОЗДАЁМ БОТА
# ============================================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ============================================
# 5. КОМАНДА /start
# ============================================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(WELCOME_TEXT)

# ============================================
# 6. КОМАНДА /top - ТАБЛИЦА ЛИДЕРОВ
# ============================================
@dp.message(Command("top"))
async def show_top(message: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # За сегодня
    cursor.execute("""
        SELECT name, SUM(count) as total 
        FROM users 
        WHERE date = ? 
        GROUP BY user_id 
        ORDER BY total DESC 
        LIMIT 10
    """, (today,))
    today_res = cursor.fetchall()

    # За неделю
    cursor.execute("""
        SELECT name, SUM(count) as total 
        FROM users 
        WHERE date >= ? 
        GROUP BY user_id 
        ORDER BY total DESC 
        LIMIT 10
    """, (week_ago,))
    week_res = cursor.fetchall()

    # За всё время
    cursor.execute("""
        SELECT name, SUM(count) as total 
        FROM users 
        GROUP BY user_id 
        ORDER BY total DESC 
        LIMIT 10
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
# 7. КОМАНДА /mystats - МОЯ СТАТИСТИКА
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

    await message.answer(
        f"📊 **МОЯ СТАТИСТИКА**\n\n"
        f"📅 Сегодня: {today_total} отжиманий\n"
        f"📆 За неделю: {week_total} отжиманий\n"
        f"🏆 Всего: {all_total} отжиманий"
    )

# ============================================
# 8. КОМАНДА /today - РЕЗУЛЬТАТЫ ЗА СЕГОДНЯ
# ============================================
@dp.message(Command("today"))
async def today_stats(message: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT name, SUM(count) as total 
        FROM users 
        WHERE date = ? 
        GROUP BY user_id 
        ORDER BY total DESC
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
# 9. КОМАНДА /reset - СБРОСИТЬ МОИ РЕЗУЛЬТАТЫ
# ============================================
@dp.message(Command("reset"))
async def reset_stats(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    await message.answer("🔄 ВСЕ ТВОИ ОТЖИМАНИЯ СБРОШЕНЫ!")

# ============================================
# 10. ОБРАБОТКА ЛЮБЫХ СООБЩЕНИЙ (ЧИСЛА)
# ============================================
@dp.message()
async def handle_numbers(message: types.Message):
    text = message.text.strip()
    
    # Разбиваем на части
    parts = text.split()
    
    # Проверяем, что все части — числа
    numbers = []
    for part in parts:
        if part.isdigit():
            numbers.append(int(part))
        else:
            await message.answer(
                "❌ Я понимаю только числа!\n\n"
                "Пример: 30  → добавить 30\n"
                "Пример: 17 13 15  → 17+13+15 = 45\n"
                "Команды: /top, /mystats, /today, /reset"
            )
            return
    
    if not numbers:
        await message.answer("❌ Отправь хотя бы одно число!")
        return
    
    # Проверяем ограничения
    for num in numbers:
        if num <= 0:
            await message.answer("❌ Числа должны быть больше 0!")
            return
        if num > 1000:
            await message.answer(f"😱 {num} слишком много! Максимум 1000.")
            return
    
    total_count = sum(numbers)
    user_id = message.from_user.id
    name = message.from_user.first_name
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Сохраняем
    for count in numbers:
        cursor.execute(
            "INSERT INTO users (user_id, name, count, date) VALUES (?, ?, ?, ?)",
            (user_id, name, count, today)
        )
    conn.commit()
    
    # Считаем сегодняшний итог
    cursor.execute(
        "SELECT SUM(count) FROM users WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    today_total = cursor.fetchone()[0] or 0
    
    # Мотивационные фразы
    phrases = [
        "💪 МОЩЬ!",
        "🔥 ОГОНЬ!",
        "🏆 ТЫ КРАСАВЧИК!",
        "⚡ НЕ ОСТАНАВЛИВАЙСЯ!",
        "🎯 ТОЧНЫЙ ВЫСТРЕЛ!",
        "💯 ИДЕАЛЬНО!",
        "🚀 ЛЕТИМ ДАЛЬШЕ!",
        "👑 ТЫ КОРОЛЬ!",
        "🎉 СУПЕР! ТАК ДЕРЖАТЬ!",
        "😤 ЕЩЁ! ЕЩЁ! ЕЩЁ!"
    ]
    phrase = random.choice(phrases)
    
    if len(numbers) == 1:
        await message.answer(
            f"✅ +{total_count} ОТЖИМАНИЙ!\n"
            f"{phrase}\n"
            f"📅 СЕГОДНЯ: {today_total} ОТЖИМАНИЙ"
        )
    else:
        numbers_str = " + ".join(str(n) for n in numbers)
        await message.answer(
            f"✅ {numbers_str} = {total_count} ОТЖИМАНИЙ!\n"
            f"{phrase}\n"
            f"📅 СЕГОДНЯ: {today_total} ОТЖИМАНИЙ"
        )

# ============================================
# 11. ЗАПУСК БОТА
# ============================================
async def main():
    print("🚀 БОТ ЗАПУЩЕН!")
    print("📱 ОТПРАВЛЯЙ ЧИСЛА: 30 ИЛИ 17 13 15")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())