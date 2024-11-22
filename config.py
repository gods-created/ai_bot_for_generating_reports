from dotenv import load_dotenv
from loguru import logger
from aiogram import Bot
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from os import getenv

load_dotenv()
bot = Bot(token=getenv('BOT_TOKEN', ''))
edit_data_url = getenv('EDIT_DATA_URL', 'http://0.0.0.0:8001/edit_data?user_id=[USER_ID]')

def options() -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    actions = [
        KeyboardButton(text='Сгенерувати звіт за допомогою ШІ'),
        KeyboardButton(text='Сгенерувати звіт і відправити на пошту'),
        KeyboardButton(text='Налаштування')
    ]

    for i in actions:
        builder.add(i)
    
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)