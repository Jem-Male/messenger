from pydantic import (
    BaseModel, 
    Field, 
    EmailStr, 
    model_validator # model_validator - для проверки обязательного одного поля из нескольких
)
from typing import (
    Annotated, # Annotated - можно прописать удобные подсказки
    Self
)
from datetime import datetime


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    email: EmailStr


class UserRegisterSchema(UserSchema):
    password: str = Field(min_length=8, description="Чистый пароль от пользователя")


class UserResponseSchema(UserSchema):
    id: int # ID генерирует база, поэтому он есть в ответе
    created_at: datetime

    class Config:
        from_attributes = True # Позволяет Pydantic читать данные из моделей SQLAlchemy


new_user = UserRegisterSchema(
    username="User-1",
    email="user1@email.com",
    password="12345678"
)

print(repr(new_user.username))