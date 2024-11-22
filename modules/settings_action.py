from copy import deepcopy 
from os import getenv
from .singleton import Singleton
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Users

class SettingsAction(Singleton):
    def __init__(self):
        super().__init__()
        self.session = None

    async def __aenter__(self):
        sqlite_connection_string = getenv('SQLITE_CONNECTION_STRING', 'sqlite:///./databases/users.db')
        if sqlite_connection_string:
            self.session = Session(
                create_engine(
                    sqlite_connection_string,
                    echo=False
                )
            )

        return self
    
    async def _select_user(self, user_id: str) -> dict:
        response_json = deepcopy(self.st_response_json)
        response_json['user'] = {}

        try:
            if not isinstance(user_id, str):
                raise ValueError('Некореткний ID користувача.')
            
            stmt = select(Users).where(Users.user_id == user_id)
            for user in self.session.scalars(stmt):
                if user.user_id == user_id:
                    response_json['status'] = 'success'
                    response_json['user'] = user.to_json()
                    break
        
        except (ValueError, Exception, ) as e:
            response_json['err_description'] = f'Увага, помилка! {str(e)}'

        finally:
            return response_json
    
    async def _insert_user(self, user_id: str) -> dict:
        response_json = deepcopy(self.st_response_json)

        try:
            if not isinstance(user_id, str):
                raise ValueError('Некореткний ID користувача.')
            
            if_user_exists = await self._select_user(user_id)
            if not if_user_exists.get('user', {}):
                new_user = Users(user_id=user_id)
                self.session.add(new_user)
                self.session.commit()

            response_json['status'] = 'success'
        
        except (ValueError, Exception, ) as e:
            response_json['err_description'] = f'Увага, помилка! {str(e)}'
            self.session.rollback()

        finally:
            return response_json
        
    async def _update_user(self, json_data: dict) -> dict:
        response_json = deepcopy(self.st_response_json)

        try:
            if not isinstance(json_data, dict):
                raise ValueError('Некоректно вказані параметри.')
            
            user_id = json_data.get('user_id', '')
            if_user_exists = await self._select_user(user_id)
            if not if_user_exists.get('user', {}):
                response_json['err_description'] = 'Користувача з таким ID не знайдено!\nПочніть знову, використав /start'
            else:
                email, report_resource = (
                    json_data.get('email', ''),
                    json_data.get('report_resource', '')
                )

                if not all((email, report_resource)):
                    raise ValueError('Для оновлення даних не вказані усі необхідні параметри.')

                self.session.query(Users).filter(Users.user_id == user_id).update({
                    Users.email: email, 
                    Users.report_resource: str(report_resource)
                })
                self.session.commit()

                response_json['status'] = 'success'
        
        except (ValueError, Exception, ) as e:
            response_json['err_description'] = f'Увага, помилка! {str(e)}'
            self.session.rollback()

        finally:
            return response_json
    
    async def __aexit__(self, *args, **kwargs):
        if self.session:
            self.session.close()