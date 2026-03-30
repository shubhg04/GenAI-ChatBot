from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_memory, build_chat_service
from schemas import ChatRequest, ChatResponse, ResetResponse
from memory_manager import MemoryManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def home():
    return {"message": "Chatbot API is running"}

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/chat", response_model = ChatResponse)
def chat(
    request: ChatRequest,
    memory: MemoryManager = Depends(get_memory)
):
    try:
        logger.info(f"/chat called with input: {request.user_input}")

        service = build_chat_service(memory)
        ChatService_Result = service.process(request.user_input)

        logger.info(f"/chat response intent: {ChatService_Result['intent']}")
        logger.info("Response generated successfully")
        
        return ChatService_Result
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.post("/reset", response_model = ResetResponse)
def reset(
    memory: MemoryManager = Depends(get_memory)
):
    try:
        logger.info("/reset called")

        memory.clear()
        return {"message": "Chat memory cleared successfully"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    