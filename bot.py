import asyncio
from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from config import bot, logger, options
from routers import settings, report_generator

from modules.settings_action import SettingsAction

dp = Dispatcher()

dp.include_router(
    settings
)

dp.include_router(
    report_generator
)

@dp.message(CommandStart())
async def _command_start(message: Message) -> None:
    user_id = str(message.from_user.id)
    user_fullname = message.from_user.full_name

    async with SettingsAction() as module:
        insert_user_response = await module._insert_user(user_id)
    
    status, err_description = (
        insert_user_response.get('status', 'error'), 
        insert_user_response.get('err_description', ''),
    )

    if status == 'error' and err_description:
        logger.error(
            err_description
        )

    await message.answer(f'Вітаю, {user_fullname}. 👋\nВикористай усі можливості цього бота. 🦾', parse_mode='HTML', reply_markup=options())

@dp.message(lambda message: not message.text in [
    'Налаштування', 'Сгенерувати звіт за допомогою ШІ', 'Сгенерувати звіт і відправити на пошту'
])
async def _none(message: Message) -> None:
    await message.answer('Такого в моїх можливостях немає!')

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(
            main()
        )

    except (KeyboardInterrupt, Exception, ) as e:
        logger.error(str(e))

    finally:
        loop.close()