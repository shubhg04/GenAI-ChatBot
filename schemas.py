from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_input: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    user_input: str 
    bot_response: str
    intent: str

class ResetResponse(BaseModel):
    message: str