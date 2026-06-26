from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class ChatRequest(BaseModel):
    message: str
    session_id: str