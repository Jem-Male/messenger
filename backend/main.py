from fastapi import FastAPI
from decimal import Decimal
from datetime import datetime, date

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

app = FastAPI(title="Messenger")

class User(BaseModel):
    user_id: int = Field(gt=0, description="Unique user ID")
    email: EmailStr
    username: str = Field(min_length=3, max_length=60)
    hashed_password: str = Field(min_length=60, max_length=60, repr=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    message_id: int = Field(gt=0)
    snder_user_id: int = Field(gt=0)
    
    # надо разобраться со стилем
    group_id: Annotated[int, Field(gt=0)] | None = None
    recipient_user_id: int | None = Field(None, gt=0) 
    
    text: str = Field(max_length=8192, repr=False)

    @model_validator(mode='after')
    def check_at_least_ine_exists(self) -> Self:
        if not self.group_id or self.recipient_user_id:
            raise ValueError()
        return self

class Group(BaseModel):
    group_id: int = Field(gt=0)
    group_name: str = Field(min_length=1, max_length=100)
    group_discription: str = Field(min_length=1, max_length=250)
    group_hidden: bool = Field(default=False)

messages = []

@app.get("/messages")
def read_messages():
    return {"messages":messages}


@app.post("/messages")
def create_messages(msg: Message):
    
    new_message = {
        "message_id": msg.message_id, 
        "snder_user_id": msg.snder_user_id,  
        "group_id": msg.group_id,
        "recipient_user_id": msg.recipient_user_id,
        "text": msg.text
    }
    messages.append(new_message)
    
    return {"Result":"success", "mes": new_message}


@app.delete("/messages/{message_id}")
def delete_messages(message_id: int):
    if message_id < 0 or message_id > len(messages):
        return {"Error": "Message not found"}
    
    deleted_message = messages.pop(message_id)
    
    return {"Result": "success", "deleted message": deleted_message}
