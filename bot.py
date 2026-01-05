from aiogram import Bot, Dispatcher, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio
import requests
import time
import uuid
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
PANEL_URL = os.getenv("PANEL_URL")
SUB_URL = os.getenv("SUB_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
INBOUND_ID = os.getenv("INBOUND_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

session = requests.Session()

# ===== Функции работы с панелью =====
def sync_login():
    url = f"{PANEL_URL}/login"
    data = {"username": USERNAME, "password": PASSWORD}
    resp = session.post(url, json=data)
    return resp.status_code == 200 and session.cookies.get("3x-ui")

def sync_add_client(username):
    url = f"{PANEL_URL}/panel/api/inbounds/addClient"
    expiry_timestamp = int(time.time()) + 30 * 86400
    user_uuid = str(uuid.uuid4())

    client = {
        "id": user_uuid,
        "email": username,
        "limitIp": 0,
        "totalGB": 0,
        "expiryTime": expiry_timestamp * 1000,
        "enable": True,
        "tgId": "",
        "subId": username,
        "reset": 0
    }

    payload = {
        "id": INBOUND_ID,
        "settings": json.dumps({"clients": [client]})
    }

    headers = {"Content-Type": "application/json"}

    resp = session.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        return True, f"{SUB_URL}/{username}"
    return False, None

async def login():
    return await asyncio.to_thread(sync_login)

async def add_client(username):
    return await asyncio.to_thread(sync_add_client, username)

# ===== FSM States =====
class AddUserStates(StatesGroup):
    waiting_for_username = State()

# ===== Обработчики бота =====
@dp.message(Command("start"))
async def start_command(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить пользователя")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)

@dp.message(F.text == "Добавить пользователя")
async def process_add_user_button(message: Message, state: FSMContext):
    await message.answer("Введите имя пользователя:")
    await state.set_state(AddUserStates.waiting_for_username)

@dp.message(StateFilter(AddUserStates.waiting_for_username))
async def handle_username(message: Message, state: FSMContext):
    username = message.text.strip()
    if not username:
        await message.answer("Имя не может быть пустым! Попробуйте снова:")
        return

    authorized = await login()
    if not authorized:
        await message.answer("Ошибка авторизации на панели VPN.")
        await state.clear()
        return

    success, link = await add_client(username)
    if success:
        await message.answer(f"Пользователь {username} добавлен!")
        await message.answer(f"Чтобы начать использовать VPN, воспользуйся <a href=\"https://teletype.in/@sorokin_xd/yZeNii7Icsz\">ИНСТРУКЦИЕЙ</a>.\n\nВот ссылка на конфигурацию:\n\n<code>{link}</code>", parse_mode="HTML")
    else:
        await message.answer("Ошибка при добавлении пользователя.")
    await state.clear()

# ===== Запуск бота =====
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))