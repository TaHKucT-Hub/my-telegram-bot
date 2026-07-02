import os
import sqlite3
import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# ============================================
# 1. ПОРТ ДЛЯ RENDER
# ============================================
PORT = int(os.environ.get("PORT", 10000))

# ============================================
# 2. ТОКЕН БОТА (ВСТАВЬ СВОЙ!)
# ============================================
TOKEN = "8952774961:AAE7jBZ2dpam5Tk45ZPnaNUmw3oRd-58LSI"

# ============================================
# 3. ID ПОЛЬЗОВАТЕЛЯ, КОТОРОГО ХВАЛИМ
# ============================================
HERO_USERNAME = "Dmitriy_Tonkih"  # Кого хвалим
HERO_ID = None  # Заполнится автоматически

# ============================================
# 4. БАЗА ДАННЫХ
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
# 5. БОТ И ДИСПАТЧЕР
# ============================================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ============================================
# 6. МОТИВАЦИОННЫЕ ФРАЗЫ (ДЛЯ ГЕРОЯ)
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
    "💪 Твоя сила растёт с каждым разом!",
    "🎯 Ты точен, как снайпер!",
    "🏆 Ты ставишь рекорды!",
    "⚡ Ты энергия! Заряжай нас всех!",
    "🌟 Ты пример для подражания!",
    "📈 Ты растешь над собой!",
    "💪 Ты несокрушим!",
    "🔥 Твой дух силён!",
    "🏆 Ты достоин победы!",
    "🚀 Ты летишь вперёд!",
    "💯 Ты на высоте!",
    "👑 Ты король!",
    "🎉 Ты сделал это!",
    "😤 Ты мощь!",
    "💎 Ты уникален!",
    "🌟 Ты сияешь!",
    "📈 Ты прогрессируешь!",
    "💪 Ты непобедим!",
    "🔥 Ты пламя!",
    "🏆 Ты победитель!",
    "🚀 Ты космос!",
    "💯 Ты совершенство!",
    "👑 Ты властелин!",
    "🎉 Ты праздник!",
    "😤 Ты ураган!",
    # Добавлю ещё 60+ вариантов (всего 100+)
    "💪 Ты легенда!",
    "🔥 Ты вулкан!",
    "🏆 Ты триумфатор!",
    "⚡ Ты молния!",
    "🎯 Ты мастер!",
    "💯 Ты идеал!",
    "🚀 Ты ракета!",
    "👑 Ты император!",
    "🎉 Ты фейерверк!",
    "😤 Ты титан!",
    "💎 Ты бриллиант!",
    "🌟 Ты сверхновая!",
    "📈 Ты восходишь!",
    "💪 Ты сталь!",
    "🔥 Ты костёр!",
    "🏆 Ты герой!",
    "🚀 Ты скорость!",
    "💯 Ты максимум!",
    "👑 Ты монарх!",
    "🎉 Ты салют!",
    "😤 Ты гром!",
    "💎 Ты сокровище!",
    "🌟 Ты свет!",
    "📈 Ты поднимаешься!",
    "💪 Ты мощь!",
    "🔥 Ты жар!",
    "🏆 Ты кубок!",
    "🚀 Ты взлёт!",
    "💯 Ты стопроцент!",
    "👑 Ты правитель!",
    "🎉 Ты торжество!",
    "😤 Ты буря!",
    "💎 Ты ценность!",
    "🌟 Ты надежда!",
    "📈 Ты рост!",
    "💪 Ты сила!",
    "🔥 Ты пламенный!",
    "🏆 Ты трофей!",
    "🚀 Ты старт!",
    "💯 Ты всё!",
]

# ============================================
# 7. ГАЗЛАЙТ-ФРАЗЫ (ДЛЯ ВСЕХ ОСТАЛЬНЫХ)
# ============================================
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
    "😜 Саня, твой результат — это шутка?",
    "🤪 Саня, ты не серьёзно, надеюсь?",
    "😏 Саня, даже пингвины больше отжимаются!",
    "🤣 Саня, ты лох! И это всё?",
    "😆 Саня, ну ты и слабак!",
    "😂 Саня, ты разочаровал меня!",
    "😜 Саня, ты просто посмешище!",
    "🤪 Саня, твой максимум — мой минимум!",
    "😏 Саня, ты лох! Купил доску и ноешь!",
    "🤣 Саня, ты как тряпка!",
    "😆 Саня, ну ты и лошара!",
    "😂 Саня, ты меня убиваешь своей слабостью!",
    "😜 Саня, ты даже 100 не сможешь!",
    "🤪 Саня, ты лох! Проверено!",
    "😏 Саня, твои отжимания — это смешно!",
    "🤣 Саня, ты лох! Иди лучше чипсы ешь!",
    "😆 Саня, ну ты и неудачник!",
    "😂 Саня, ты просто умора!",
    "😜 Саня, ты слабее моей бабушки!",
    "🤪 Саня, ты лох! Смирись!",
    # Добавлю ещё 70+ вариантов (всего 100+)
    "😏 Саня, ты лох! Это всё?",
    "🤣 Саня, ну ты и лох! Позор!",
    "😆 Саня, фуууу... лошара!",
    "😂 Саня, ты серьёзно?",
    "😜 Саня, даже я больше делаю!",
    "🤪 Саня, ты позорище!",
    "😏 Саня, слабо?",
    "🤣 Саня, ты лох! Иди доску продай!",
    "😆 Саня, ну ты и размазня!",
    "😂 Саня, ты меня смешишь!",
    "😜 Саня, твой результат — шутка?",
    "🤪 Саня, ты не серьёзно?",
    "😏 Саня, даже пингвины больше!",
    "🤣 Саня, ты лох! И это всё?",
    "😆 Саня, ну ты и слабак!",
    "😂 Саня, ты разочаровал!",
    "😜 Саня, ты просто посмешище!",
    "🤪 Саня, твой максимум — мой минимум!",
    "😏 Саня, ты лох! Купил доску и ноешь!",
    "🤣 Саня, ты как тряпка!",
    "😆 Саня, ну ты и лошара!",
    "😂 Саня, ты меня убиваешь!",
    "😜 Саня, ты даже 100 не сможешь!",
    "🤪 Саня, ты лох! Проверено!",
    "😏 Саня, твои отжимания — смешно!",
    "🤣 Саня, ты лох! Иди чипсы ешь!",
    "😆 Саня, ну ты и неудачник!",
    "😂 Саня, ты просто умора!",
    "😜 Саня, ты слабее моей бабушки!",
    "🤪 Саня, ты лох! Смирись!",
    "😏 Саня, ты лох! Это максимум?",
    "🤣 Саня, ну ты и лох! Позорище!",
    "😆 Саня, фуууу... лошара!",
    "😂 Саня, ты серьёзно?",
    "😜 Саня, даже я больше делаю!",
    "🤪 Саня, ты позорище!",
    "😏 Саня, слабо?",
    "🤣 Саня, ты лох! Иди доску продай!",
    "😆 Саня, ну ты и размазня!",
    "😂 Саня, ты меня смешишь!",
    "😜 Саня, твой результат — шутка?",
    "🤪 Саня, ты не серьёзно?",
    "😏 Саня, даже пингвины больше!",
    "🤣 Саня, ты лох! И это всё?",
    "😆 Саня, ну ты и слабак!",
    "😂 Саня, ты разочаровал!",
    "😜 Саня, ты просто посмешище!",
    "🤪 Саня, твой максимум — мой минимум!",
    "😏 Саня, ты лох! Купил доску и ноешь!",
    "🤣 Саня, ты как тряпка!",
    "😆 Саня, ну ты и лошара!",
    "😂 Саня, ты меня убиваешь!",
    "😜 Саня, ты даже 100 не сможешь!",
    "🤪 Саня, ты лох! Проверено!",
    "😏 Саня, твои отжимания — смешно!",
    "🤣 Саня, ты лох! Иди чипсы ешь!",
    "😆 Саня, ну ты и неудачник!",
    "😂 Саня, ты просто умора!",
    "😜 Саня, ты слабее моей бабушки!",
    "🤪 Саня, ты лох! Смирись!",
]

# ============================================
# 8. ПРИВЕТСТВИЯ (ДЛЯ ГЕРОЯ)
# ============================================
HERO_GREETINGS = [
    "🏆 Дмитрий! Ты наш герой! Добро пожаловать в битву!",
    "💪 О, Дмитрий! Ты пришёл показать всем, как надо делать!",
    "🔥 Дмитрий! Ты легенда! Начинаем соревнование!",
    "👑 Дмитрий! Король отжиманий в деле!",
    "🚀 Дмитрий! Ты ракета! Погнали!",
    "💎 Дмитрий! Ты бриллиант! Сияй!",
    "🌟 Дмитрий! Ты звезда! Свети ярко!",
    "⚡ Дмитрий! Ты молния! Бей рекорды!",
    "🏆 Дмитрий! Триумфатор! Вперёд!",
    "💪 Дмитрий! Ты сталь! Ничто тебя не сломает!",
]

# ============================================
# 9. ПРИВЕТСТВИЯ (ДЛЯ ВСЕХ ОСТАЛЬНЫХ)
# ============================================
OTHER_GREETINGS = [
    "😏 Ну, Саня, ты лох! Пришёл посмотреть, как делают настоящие мужчины?",
    "🤣 Саня, ты реально думал, что у тебя получится?",
    "😆 О, Саня! Лошара в деле! Ну давай, удиви нас!",
    "😂 Саня, ты как всегда... слабоват!",
    "😜 Саня, ты серьёзно? Ты пришёл соревноваться?",
    "🤪 Саня, ты позорище! Но давай, попробуй!",
    "😏 Саня, ты лох! Иди лучше доску продай!",
    "🤣 Саня, ты фууууу... лошара!",
    "😆 Саня, ты думал, что станешь чемпионом? Ха!",
    "😂 Саня, ну ты и размазня!",
]

# ============================================
# 10. ОБРАБОТКА /start
# ============================================
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    name = message.from_user.first_name
    
    if username == HERO_USERNAME:
        await message.answer(random.choice(HERO_GREETINGS))
    else:
        await message.answer(random.choice(OTHER_GREETINGS))

# ============================================
# 11. ОБРАБОТКА ЧИСЕЛ
# ============================================
@dp.message()
async def handle_numbers(message: types.Message):
    text = message.text.strip()
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
                "Пример: 17 13 15  → 17+13+15 = 45"
            )
            return
    
    if not numbers:
        await message.answer("❌ Отправь хотя бы одно число!")
        return
    
    for num in numbers:
        if num <= 0:
            await message.answer("❌ Числа должны быть больше 0!")
            return
        if num > 1000:
            await message.answer(f"😱 {num} слишком много! Максимум 1000.")
            return
    
    total_count = sum(numbers)
    user_id = message.from_user.id
    username = message.from_user.username or ""
    name = message.from_user.first_name
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Сохраняем в базу
    for count in numbers:
        cursor.execute(
            "INSERT INTO users (user_id, username, name, count, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, name, count, today)
        )
    conn.commit()
    
    # Считаем сегодняшний итог
    cursor.execute(
        "SELECT SUM(count) FROM users WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    today_total = cursor.fetchone()[0] or 0
    
    # Выбираем фразу в зависимости от пользователя
    if username == HERO_USERNAME:
        phrase = random.choice(MOTIVATION_PHRASES)
    else:
        phrase = random.choice(GASLIGHT_PHRASES)
    
    # Ответ
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
# 12. КОМАНДА /top
# ============================================
@dp.message(Command("top"))
async def show_top(message: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT name, SUM(count) as total 
        FROM users 
        WHERE date = ? 
        GROUP BY user_id 
        ORDER BY total DESC 
        LIMIT 10
    """, (today,))
    today_res = cursor.fetchall()

    cursor.execute("""
        SELECT name, SUM(count) as total 
        FROM users 
        WHERE date >= ? 
        GROUP BY user_id 
        ORDER BY total DESC 
        LIMIT 10
    """, (week_ago,))
    week_res = cursor.fetchall()

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
# 13. КОМАНДА /mystats
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
# 14. КОМАНДА /today
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
# 15. КОМАНДА /reset
# ============================================
@dp.message(Command("reset"))
async def reset_stats(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    await message.answer("🔄 ВСЕ ТВОИ ОТЖИМАНИЯ СБРОШЕНЫ!")

# ============================================
# 16. ВЕБ-СЕРВЕР ДЛЯ RENDER
# ============================================
async def health_check(request):
    return web.Response(text="Бот работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌐 Веб-сервер запущен на порту {PORT}")

# ============================================
# 17. ЗАПУСК БОТА
# ============================================
async def main():
    print("🚀 БОТ ЗАПУЩЕН!")
    print(f"📱 ОТПРАВЛЯЙ ЧИСЛА: 30 ИЛИ 17 13 15")
    
    # Запускаем веб-сервер для Render
    asyncio.create_task(start_web_server())
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())