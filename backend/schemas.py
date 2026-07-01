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

class UserRegisterSchema(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, description="Чистый пароль от пользователя")

class UserResponseSchema(BaseModel):
    id: int # ID генерирует база, поэтому он есть в ответе
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True # Позволяет Pydantic читать данные из моделей SQLAlchemy


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Пароль от пользователя")


class MessageCreateSchema(BaseModel):
    message_id: int = Field(gt=0)
    snder_user_id: int = Field(gt=0)
    
    # надо разобраться со стилем
    # group_id: Annotated[int, Field(gt=0)] | None = None
    group_id: int | None =  Field(default=None, gt=0)
    recipient_user_id: int | None = Field(None, gt=0) 
    
    text: str = Field(max_length=8192, repr=False)

    @model_validator(mode='after')
    def check_at_least_ine_exists(self) -> Self:
        if not self.group_id and not self.recipient_user_id:
            raise ValueError("Error")
        return self


class GroupSchema(BaseModel):
    group_id: int = Field(gt=0)
    group_name: str = Field(min_length=1, max_length=100)
    group_discription: str = Field(min_length=1, max_length=250)
    group_hidden: bool = Field(default=False)
