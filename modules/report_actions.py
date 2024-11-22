from random import choice
from string import ascii_letters, digits
from os import getenv, getcwd, remove
from openai import OpenAI
from copy import deepcopy
from aiohttp import ClientSession
from csv import writer
from py_csv_xls import CSVSniffer, ExcelWorker
from ast import literal_eval

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from .singleton import Singleton
from .settings_action import SettingsAction

class ReportActions(Singleton):
    def __init__(self):
        super().__init__()
        self.openai = None
        self.st_response_json['data'] = ''

    async def __aenter__(self):
        openai_api_key = getenv('OPENAI_API_KEY', '')
        if openai_api_key:
            self.openai = OpenAI(api_key=openai_api_key)

        return self
    
    def __send_report_to_email(self, data: str, user_email: str) -> dict:
        response_json = deepcopy(self.st_response_json)

        try:
            sender_email = getenv('SMTP_SENDER_EMAIL', '')
            sender_password = getenv('SMTP_SENDER_PASSWORD', '')

            if not all((sender_email, sender_password)):
                response_json['err_description'] = 'Можливість відправляти звіти на пошту наразі відсутня.'
                return response_json

            subject = 'Твій звіт від бота'
            body = ''
            sender_email = getenv('SMTP_SENDER_EMAIL', '')
            recipient_email = user_email
            smtp_server = 'smtp.gmail.com'
            smtp_port = 465
            message = MIMEMultipart()

            message['Subject'] = subject
            message['From'] = sender_email
            message['To'] = recipient_email
            body_part = MIMEText(body)
            message.attach(body_part)

            with open(data, mode='rb') as file:
                message.attach(MIMEApplication(file.read(), Name="report.xls"))

            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())

            response_json['status'] = 'success'
            
        except (Exception, ) as e:
            response_json['err_description'] = f'Увага, помилка! {str(e)}'

        finally:
            return response_json
    
    def __converter(self, csv_file: str, excel_filename: str) -> None:
        file_lines = CSVSniffer(
            main_path=csv_file,
        ).get_dir_files_with_lines()

        ExcelWorker(
            workbook_name=excel_filename,
            workbook_extension='.xls',
            want_cleared=True,
        ).fill_workbook(all_data=file_lines)

        remove(csv_file)
        return None
    
    def __filenames_generator(self) -> list:
        return [
            ''.join(choice(ascii_letters + digits) for _ in range(10)),
            ''.join(choice(ascii_letters + digits) for _ in range(10))
        ]

    async def __ai_worker(self, data: str) -> dict:
        response_json = deepcopy(self.st_response_json)

        try:
            response = self.openai.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            'Ты профессиональный аналитик данных. Твоя задача - анализировать входящие данные '
                            'и генерировать результат в формате списка списков для Python. Каждый вложенный список '
                            'представляет строку таблицы, а его элементы - ячейки. Первая строка должна быть '
                            'заголовком с названиями колонок. Не добавляй лишнего текста, только список данных (и без markdown).'
                        )
                    },
                    {
                        'role': 'user',
                        'content': data
                    }
                ]
            )

            content = response.choices[0].message.content
            data_list = literal_eval(content.strip())

            csv_filename, excel_filename, *_ = self.__filenames_generator()
            csv_file = csv_filename + '.csv'
            with open(csv_file, mode='w') as f:
                csvwriter = writer(f)
                csvwriter.writerows(data_list)

            self.__converter(csv_file, excel_filename)
            excel_file = excel_filename + '.xls'

            response_json['data'] = f'{getcwd()}/{excel_file}'
            response_json['status'] = 'success'
            
        except (Exception, ) as e:
            response_json['err_description'] = f'Увага, помилка! {str(e)}'

        finally:
            return response_json

    async def __get_report_data(self, url: str) -> dict:
        response_json = deepcopy(self.st_response_json)

        try:
            async with ClientSession() as session:
                async with session.get(url, headers={}) as request:
                    status = request.status
                    if status not in [200, 201]:
                        err_description = f'Джерело звіту повернуло полмилку (<b>{status}</b>). Перевірте чи все вірно!'
                        response_json['err_description'] = err_description
                        return response_json
                    
                    response = await request.text()

            response_json['data'] = response
            response_json['status'] = 'success'
            
        except (Exception, ) as e:
            response_json['err_description'] = f'Увага, помилка! {str(e)}'

        finally:
            return response_json
    
    async def _generate_report(self, user_id: str, send_to_email: bool = False) -> dict:
        response_json = deepcopy(self.st_response_json)

        try:
            if not isinstance(user_id, str):
                raise ValueError('Некореткний ID користувача.')
            
            async with SettingsAction() as module:
                select_user_response = await module._select_user(user_id)

            user_data = select_user_response.get('user', {})
            user_email = user_data.get('email', '')
            report_resource = user_data.get('report_resource', '')

            if not user_data:
                response_json['err_description'] = 'Користувача з таким ID не знайдено!\nПочніть знову, використав /start'
            elif not report_resource:
                response_json['err_description'] = 'Ви ще вказали джерело звіту. Використайте налаштування для зміни персональних даних.'
            else:
                report_data = await self.__get_report_data(report_resource)
                if report_data.get('status', 'error') == 'error':
                    response_json.update(report_data)
                    return response_json
                
                data = report_data.get('data')

                ai_worker_response = await self.__ai_worker(data)
                if ai_worker_response.get('status', 'error') == 'error':
                    response_json.update(ai_worker_response)
                    return response_json
                
                data = ai_worker_response.get('data')
                if send_to_email:
                    if not user_email:
                        response_json['err_description'] = 'Ви ще вказали свою пошту. Використайте налаштування для зміни персональних даних.'
                        return response_json
                    
                    send_to_email_response = self.__send_report_to_email(data, user_email)
                    response_json.update(send_to_email_response)
                    remove(data)
                    return response_json

                response_json['data'] = data
                response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = f'Увага, помилка! {str(e)}'

        finally:
            return response_json
    
    async def __aexit__(self, *args, **kwargs):
        if self.openai:
            self.openai.close()