from fastapi import FastAPI
from pydantic import BaseModel
from assistant import chat

app = FastAPI()

class Msg(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat_endpoint(m: Msg):
    return {"reply": chat(m.user_id, m.message)}