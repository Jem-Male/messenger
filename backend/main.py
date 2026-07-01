import code
from pydantic import HttpUrl
from alembic.util import status
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext

from database import async_session_maker
from models import User
from schemas import (
    UserRegisterSchema,
    UserResponseSchema,
    UserLoginSchema,
    MessageCreateSchema
)

app = FastAPI(title="Messenger")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_db():
    async with async_session_maker() as session:
        yield session # Выдает сессию на время запроса, а потом автоматически закрывает

messages = []


# response_model=UserResponseSchema говорит FastAPI: "Отфильтруй ответ через эту схему"
@app.post("/register", response_model=UserResponseSchema)
async def register_user(
    user_data: UserRegisterSchema,
    session: AsyncSession = Depends(get_db)
):
    
    # 1. Проверяем, нет ли уже такого email в базе
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    if result.scalars().first() is not None:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    

    hashed_pwd = get_password_hash(user_data.password)
    
    new_user = User(
        username = user_data.username,
        email = user_data.email,
        hashed_password = hashed_pwd
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return new_user


@app.post("/login", response_model=UserResponseSchema)
async def login_user(
    user_data: UserLoginSchema,
    session: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    user_db = result.scalars().first()
    
    if user_db is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not verify_password(user_data.password, user_db.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return user_db
    

@app.get("/messages")
def read_messages():
    return {"messages":messages}


@app.post("/messages")
def create_messages(msg: MessageCreateSchema):
    
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
