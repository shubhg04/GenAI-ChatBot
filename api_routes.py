from fastapi import APIRouter, HTTPException, Depends
from dependencies import get_memory, build_chat_service
from schemas import ChatRequest, ChatResponse, ResetRequest, ResetResponse
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def home():
    return {"message": "Chatbot API is running"}

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/chat", response_model = ChatResponse)
def chat(request: ChatRequest):
    request_id = str(uuid.uuid4())
    try:
        logger.info(f"Request ID: {request_id} - Received input for session: {request.session_id}")

        memory = get_memory(request.session_id)
        service = build_chat_service(memory)

        ChatService_Result = service.process(
            request.user_input, 
            request.session_id,
            request_id
        )

        ChatService_Result["request_id"] = request_id

        logger.info(f"Request ID: {request_id} - Sending response for session: {request.session_id}")

        return ChatService_Result
    
    except ValueError as ve:
        logger.exception(f"Request ID: {request_id} - Validation error in /chat")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as error:
        logger.exception(f"Request ID: {request_id} - Unexpected error in /chat")
        raise HTTPException(status_code=500, detail=str(error))

@router.post("/reset", response_model = ResetResponse)
def reset(request: ResetRequest):
    try:
        logger.info(f"/reset called for session: {request.session_id}")

        memory = get_memory(request.session_id)
        memory.clear()

        return {
            "message": "Chat memory cleared successfully",
            "session_id": request.session_id
        }
    
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    