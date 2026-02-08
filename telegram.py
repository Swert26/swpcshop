import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup
from aiogram.filters import Command
import random, sqlite3, os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from database import Database, products

global login1
login1 = False
global login2
login2 = False
global user_id
user_id = 0
global user_name
user_name = ""
global logined
logined = False
global zakazed
zakazed = False

db = Database()

TOKEN = "8380303413:AAG3zInLaPMvFJzwQ0-fY-vgRwQe91vmBgE"
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(f"Привет {message.from_user.full_name}\nДля привязки аккаунта введи /login\n/zakaz для заказа")

@dp.message(Command("login"))
async def login(message: Message):
    await message.answer(f"Введите имя пользователя")
    global login1
    login1 = True

@dp.message(Command("zakaz"))
async def zakaz(message: Message):
    global logined
    if logined == False:
        await message.answer(f"Вы не привязали аккаунт\nИспользуйте /login для привязки аккаунта")
    else:
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{products[1]["name"]}", callback_data="say_one")],
        [InlineKeyboardButton(text=f"{products[2]["name"]}", callback_data="say_two")],
        [InlineKeyboardButton(text=f"{products[3]["name"]}", callback_data="say_three")],
    ])
    await message.answer("Выбор товар:", reply_markup=inline_kb)

@dp.callback_query(F.data == "say_one")
async def first_callback(callback: CallbackQuery):
    global zakazed
    zakazed = True
    await callback.message.answer(f"Продукт: {products[1]["name"]}\nВведите название города")
    await callback.answer()

@dp.callback_query(F.data == "say_two")
async def second_callback(callback: CallbackQuery):
    global zakazed
    zakazed = True
    await callback.message.answer(f"Продукт: {products[2]["name"]}\nВведите название города")
    await callback.answer()

@dp.callback_query(F.data == "say_three")
async def third_callback(callback: CallbackQuery):
    global zakazed
    zakazed = True
    await callback.message.answer(f"Продукт: {products[3]["name"]}\nВведите название города")
    await callback.answer()

@dp.message()
async def echo(message: Message):
    global login1, login2, user_name, user_id, logined, zakazed
    if login1 == True:
        con = db.get_db()
        if not db.check_user(message.text):
            await message.answer(f"Неккоректное имя пользователя: {message.text}")
        else:
            user_data = con.execute("""SELECT * FROM users WHERE name = ?""", (message.text, )).fetchone()
            user_id = user_data[0]
            user_name = user_data[1]
            login1 = False
            login2 = True
            await message.answer(f"Аккаунт: {user_name}({user_id})\nВведите пароль")
    if login2 == True:
        con = db.get_db()
        user_data = con.execute("""SELECT * FROM users WHERE name = ?""", (user_name, )).fetchone()
        if not check_password_hash(user_data[2], message.text):
            await message.answer("Неверный пароль")
        else:
            await message.answer("Аккаунт привязан")
            logined = True
            login2 = False
    if zakazed == True:
        zakazed = False
        await message.answer(f"Заказ выполнен в город {message.text}")

async def main():
    await dp.start_polling(bot)

print("работает")
asyncio.run(main())