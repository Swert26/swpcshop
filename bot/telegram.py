import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import random, sqlite3, os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from core.database import Database, products
from aiogram.client.session.aiohttp import AiohttpSession
import logging

db = Database()
TOKEN = "8294697310:AAF37z6Th5BCHPmULxDOqmCaew1dDR2NZ8w"

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

user_auth_status = {}

class LinkStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_token = State()

class OrderStates(StatesGroup):
    waiting_for_city = State()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(f"Привет {message.from_user.full_name}\nДля привязки аккаунта введи /link\nДля получения товаров /give\nВНИМАНИЕ ДАННЫЙ БОТ ЯВЛЯЕТСЯ ТЕСТОВЫМ И НЕ СОДЕРЖИТ ПЛАТЁЖНЫХ СИСТЕМ ИЛИ СКАМ СИСТЕМ")

@dp.message(Command("link"))
async def login(message: Message, state: FSMContext):
    await state.set_state(LinkStates.waiting_for_username)
    await message.answer(f"Введите имя пользователя (логин)")

@dp.message(Command("give"))
async def zakaz(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if not user_auth_status.get(user_id, False):
        await message.answer(f"Вы не привязали аккаунт\nИспользуйте /link для привязки аккаунта")
    else:
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{products[1]['name']}", callback_data="product_1")],
            [InlineKeyboardButton(text=f"{products[2]['name']}", callback_data="product_2")],
            [InlineKeyboardButton(text=f"{products[3]['name']}", callback_data="product_3")],
        ])
        await message.answer("Выберите товар:", reply_markup=inline_kb)

@dp.message(LinkStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    username = message.text.strip()
    con = db.get_db()
    
    if not db.check_user(username):
        await message.answer(f"Пользователь с именем '{username}' не найден\nПопробуйте снова или введите /link заново")
        return
    
    user_data = con.execute("""SELECT * FROM users WHERE name = ?""", (username,)).fetchone()
    
    if user_data:
        await state.update_data(user_id=user_data[0], username=user_data[1])
        await state.set_state(LinkStates.waiting_for_token)
        await message.answer(f"Аккаунт: {user_data[1]} (ID: {user_data[0]})\n\nВведите токен доступа\n⚠ ВНИМАНИЕ: НИКОМУ НЕ СООБЩАЙТЕ ТОКЕН СЕССИИ, ДАЖЕ РАЗРАБОТЧИКАМ ЭТОГО БОТА!!! ⚠")
    else:
        await message.answer("Ошибка при получении данных пользователя")

@dp.message(LinkStates.waiting_for_token)
async def process_token(message: Message, state: FSMContext):
    token = message.text.strip()
    user_data = await state.get_data()
    
    con = db.get_db()
    db_user = con.execute("""SELECT * FROM users WHERE name = ?""", (user_data['username'],)).fetchone()
    
    if not db_user:
        await message.answer("Ошибка: пользователь не найден. Используйте /link заново")
        await state.clear()
        return
    
    if token == db_user[4]:
        user_auth_status[message.from_user.id] = True
        
        new_token = db.token_gen()
        db.set_token(new_token, db_user[1])
        
        await message.answer("✅ Аккаунт успешно привязан! Теперь вы можете использовать /give для получения товаров")
        await state.clear()
    else:
        await message.answer("❌ Неверный токен. Попробуйте снова или используйте /link для повторной привязки")

@dp.callback_query(F.data.startswith("product_"))
async def product_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if not user_auth_status.get(user_id, False):
        await callback.message.answer("❌ Вы не авторизованы. Используйте /link")
        await callback.answer()
        return
    
    product_map = {
        "product_1": products[1]["name"],
        "product_2": products[2]["name"],
        "product_3": products[3]["name"]
    }
    
    selected_product = product_map.get(callback.data)
    
    if selected_product:
        await state.update_data(selected_product=selected_product)
        await state.set_state(OrderStates.waiting_for_city)
        await callback.message.answer(f"Товар: {selected_product}\n\nВведите название города для доставки:")
    else:
        await callback.message.answer("Ошибка при выборе товара")
    
    await callback.answer()

@dp.message(OrderStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    user_id = message.from_user.id
    city = message.text.strip()
    
    if not user_auth_status.get(user_id, False):
        await message.answer("❌ Вы не авторизованы. Используйте /link")
        await state.clear()
        return
    
    user_data = await state.get_data()
    selected_product = user_data.get('selected_product', 'товар')
    
    await message.answer(f"✅ Заказ оформлен!\n\nТовар: {selected_product}\nГород доставки: {city}\n\nСпасибо за покупку!")
    
    await state.clear()
@dp.message(Command("logout"))
async def logout(message: Message):
    user_id = message.from_user.id
    if user_id in user_auth_status:
        del user_auth_status[user_id]
        await message.answer("✅ Вы вышли из аккаунта")
    else:
        await message.answer("Вы не были авторизованы")

async def main():
    print("Бот запущен и работает...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())