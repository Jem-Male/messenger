from fastapi import FastAPI
from decimal import Decimal
from datetime import datetime, date
from schemas import UserSchema, GroupSchema, MessageCreateSchema

app = FastAPI(title="Messenger")


messages = []

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