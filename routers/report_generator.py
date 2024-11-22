from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from config import bot, options
from modules.report_actions import ReportActions
from os import remove 

report_generator = Router(name='report_generator')

async def _report_generator(user_id: str, send_to_email: bool = False) -> list:
    async with ReportActions() as module:
        generate_report_response = await module._generate_report(
            str(user_id), send_to_email
        )
    
    status, err_description, data = (
        generate_report_response.get('status', 'error'), 
        generate_report_response.get('err_description', ''),
        generate_report_response.get('data', {})
    )

    return [
        status, err_description, data
    ]

@report_generator.message(F.text == 'Сгенерувати звіт за допомогою ШІ')
async def _report_generator_without_sending_to_email(message: Message):
    user_id = message.from_user.id

    await message.answer('Будь-ласка, почекайте! ⏰')

    status, err_description, data, *_ = await _report_generator(user_id)

    if status == 'success' and data:
        await bot.send_document(chat_id=user_id, document=FSInputFile(data))
        remove(data)

    elif err_description:
        await message.answer(err_description, parse_mode='HTML', reply_markup=options())
    
    else:
        await message.answer('Користувача з таким ID не знайдено!\nПочніть знову, використав /start', reply_markup=options())
    
@report_generator.message(F.text == 'Сгенерувати звіт і відправити на пошту')
async def _report_generator_with_sending_to_email(message: Message):
    user_id = message.from_user.id

    await message.answer('Будь-ласка, почекайте! ⏰')

    status, err_description, data, *_ = await _report_generator(user_id, True)

    if status == 'success':
        await message.answer('Звіт відправлено на пошту. 🎉', parse_mode='HTML', reply_markup=options())

    elif err_description:
        await message.answer(err_description, parse_mode='HTML', reply_markup=options())
    
    else:
        await message.answer('Користувача з таким ID не знайдено!\nПочніть знову, використав /start', reply_markup=options())
    