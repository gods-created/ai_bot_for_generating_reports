from aiogram import Router, F
from aiogram.types import Message

from config import logger, options, edit_data_url
from modules.settings_action import SettingsAction

settings = Router(name='settings')

@settings.message(F.text == 'Налаштування')
async def _settings(message: Message):
    user_id = str(message.from_user.id)
    async with SettingsAction() as module:
        select_user_response = await module._select_user(user_id)
    
    status, err_description, user = (
        select_user_response.get('status', 'error'), 
        select_user_response.get('err_description', ''),
        select_user_response.get('user', {})
    )

    response_message = ''
    if status == 'success' and user:
        user_id, email, report_resource, created_at = (
            user.get('user_id', ''),
            user.get('email', ''),
            user.get('report_resource', ''),
            user.get('created_at', '')
        )
        for_edit_data = edit_data_url.replace('[USER_ID]', user_id)

        response_message = f'Ваш Telegram ID: <b>{user_id}</b>\n' \
                           f'Ваша пошта: <b>{email}</b>\n' \
                           f'Джерело для генерування звітів: <b>{report_resource}</b>\n' \
                           f'Профіль створено: <b>{created_at}</b>\n\n' \
                           f'Для редагування таких даних, як <b>пошта</b> і <b>джерело звітів</b>, перейдіть по посиланню:\n<b>{for_edit_data}</b>' 
        
    elif not user:
        response_message = 'Користувача з таким ID не знайдено!\nПочніть знову, використав /start'

    if err_description:
        logger.error(err_description)

    await message.answer(response_message, parse_mode='HTML', reply_markup=options())