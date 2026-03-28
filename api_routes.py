from fastapi import APIRouter, HTTPException
from dependencies import memory, service
from schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Chatbot API is running"}

@router.post("/chat", response_model = ChatResponse)
def chat(request: ChatRequest):
    try:
        bot_response = service.process(request.message)
        return bot_response
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
@router.post("/reset")
def reset():
    try:
        memory.clear()
        return {"message": "Chat memory cleared successfully"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))