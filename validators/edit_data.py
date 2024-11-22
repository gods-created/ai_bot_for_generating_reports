from pydantic import BaseModel, EmailStr, AnyHttpUrl, Field, field_validator

class Data(BaseModel):
    user_id: str = Field(default='725515777', min_length=9)
    email: EmailStr = Field(default='example@gmail.com')
    report_resource: AnyHttpUrl = Field(default='https://example.com')

    @field_validator('user_id')
    def user_id_validator(cls, value):
        if len(value) < 9:
            raise ValueError('Некоректний ID користувача.')
        
        return value

    def to_json(self) -> dict:
        return {
            'user_id': self.user_id,
            'email': self.email,
            'report_resource': self.report_resource
        }