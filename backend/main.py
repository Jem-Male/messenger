import code
from pydantic import HttpUrl
from alembic.util import status
from fastapi import(
    FastAPI, 
    Depends, 
    HTTPException, 
    Response, 
    Request,
    WebSocket,
    WebSocketDisconnect 
)
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

from database import async_session_maker
from models import User
from schemas import (
    UserRegisterSchema,
    UserResponseSchema,
    UserLoginSchema,
    MessageCreateSchema
)

app = FastAPI(title="Messenger")

SECRET_KEY = "super-secret-discord-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Токен будет жить 7 дней

def create_access_token(data: dict):
    to_encode = data.copy()
    # Устанавливаем время жизни токена (exp - это стандартное поле в JWT)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # генерация токена
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_db():
    async with async_session_maker() as session:
        yield session # Выдает сессию на время запроса, а потом автоматически закрывает


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    # достаем токен из куки
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="You are not logged in")
    
    try:
        # проверка: расшифровка токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Malformed  token")
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401,detail="Invalid token")

    query = select(User).where(User.id == int(user_id))
    result = await session.execute(query)
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User deleted or not found")
    
    return user
    
messages = []


class ConnectionManager:
    def __init__(self):
        # храним активные подключения
        self.active_connections: list[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept() # Принимаем подключение
        self.active_connections.append(websocket) # Сохраняем клиента
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket) # удаляем клиента
        
    async def broadcast(self, message: str):
        # рассылка сообщения всем клиентам
        for connection in self.active_connections:
            await connection.send_text(message) 
                      
# Общий экземпляр менеджера
manager = ConnectionManager() 


html_page = """
<!DOCTYPE html>
<html>
    <head>
        <title>Чат</title>
    </head>
    <body>
        <h1>Тестовый Чат</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Отправить</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            // Подключаемся к нашему вебсокету!
            var ws = new WebSocket("ws://localhost:5000/ws/chat");
            
            // Что делать, когда пришло сообщение от сервера
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            
            // Что делать при нажатии на кнопку
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value) // Отправляем на сервер
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/chat-test")
async def get_chat_page():
    return HTMLResponse(html_page)


@app.get("/")
async def welcome():
    return {"Result": "True"}

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


@app.post("/login")
async def login_user(
    user_data: UserLoginSchema,
    response: Response, # Внедряем объект Response, чтобы управлять Куками
    session: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    user_db = result.scalars().first()
    
    if user_db is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not verify_password(user_data.password, user_db.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token = create_access_token(data={"sub": str(user_db.id)})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,   # JS на фронтенде не сможет украсть куки
        secure=False,   #  На продакшене (HTTPS) нужно ставить True
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"message":"True result"}


@app.get('/users/me', response_model=UserResponseSchema)
async def read_user_me(
    current_user: User = Depends(get_current_user)
):
    # что то здесь
    return current_user
    

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    # клинет подключился:
    await manager.connect(websocket)
    try:
        # Запускаем бесконечный цикл прослушивания этой "трубки"
        while True:
            # ждем пока клиент что то напишет
            data = await websocket.receive_text()
            # если кто то написал то рассылаем это остальным
            await manager.broadcast(f"Аноним: {data}")
    
    except WebSocketDisconnect:
        # если клиент отключился
        manager.disconnect(websocket)
        await manager.broadcast("Кто то покинул чать")


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
