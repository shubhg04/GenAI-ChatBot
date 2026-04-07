from fastapi import APIRouter, HTTPException, Request
from dependencies import get_memory, build_chat_service, reload_retriever
from feedback_manager import FeedbackManager
from build_knowledge_base import build_knowledge_base
import logging
from schemas import (
    ChatRequest, 
    ChatResponse, 
    ResetRequest, 
    ResetResponse, 
    FeedbackRequest, 
    FeedbackSummaryResponse, 
    BuildKnowledgeBaseResponse
)


logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", tags=["General"])
def home():
    return {"message": "Chatbot API is running"}

@router.get("/health", tags=["General"])
def health_check():
    return {"status": "ok"}

@router.post("/chat", response_model = ChatResponse, tags=["Chat"])
def chat(request: ChatRequest, http_request: Request):
    request_id = http_request.state.request_id
    try:
        logger.info(f"Request ID: {request_id} - Received input for session: {request.session_id}")

        memory = get_memory(request.session_id)
        service = build_chat_service(memory)

        ChatService_Result = service.process(
            request.user_input, 
            request.session_id,
            request_id,
            use_rag = request.use_rag,
            debug = request.debug
        )

        logger.info(f"Request ID: {request_id} - Sending response for session: {request.session_id}")

        return ChatService_Result
    
    except ValueError as ve:
        logger.exception(f"Request ID: {request_id} - Validation error in /chat")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as error:
        logger.exception(f"Request ID: {request_id} - Unexpected error in /chat")
        raise HTTPException(status_code=500, detail=str(error))

@router.post("/reset", response_model = ResetResponse, tags=["Chat"])
def reset(request: ResetRequest, http_request: Request):
    request_id = http_request.state.request_id

    try:
        logger.info(
            f"Request ID: {request_id} - /reset called for session: {request.session_id}"
        )

        memory = get_memory(request.session_id)
        memory.clear()

        logger.info(
            f"Request ID: {request_id} - Memory cleared successfully for session: {request.session_id}"
        )
        
        return {
            "message": "Chat memory cleared successfully",
            "session_id": request.session_id,
        }
    
    except Exception as error:
        logger.exception(
            f"Request ID: {request_id} - Unexpected error in /reset"
        )
        raise HTTPException(status_code=500, detail=str(error))
    
@router.post("/feedback", tags=["Feedback"])
def submit_feedback(request: FeedbackRequest, http_request: Request):

    request_id = http_request.state.request_id

    try:
        logger.info(
            f"Request ID: {request_id} - Feedback received for session: {request.session_id} (request: {request.request_id})"
        )

        feedback_manager = FeedbackManager()

        entry = feedback_manager.create_feedback_entry(
            session_id = request.session_id,
            request_id = request.request_id,
            rating = request.rating,
            comments = request.comments
        )

        feedback_manager.save_feedback(entry)

        logger.info(
            f"Request ID: {request_id} - Feedback saved successfully for targer request: {request.request_id}"
        )

        return {
            "message": "Feedback submitted successfully",
        }
    
    except Exception as error:
        logger.exception(
            f"Request ID: {request_id} - Error while saving feedback"
        )
        raise HTTPException(status_code=500, detail=str(error))
    
@router.get("/feedback/summary", response_model = FeedbackSummaryResponse, tags=["Feedback"])
def feedback_summary(http_request: Request):
    request_id = http_request.state.request_id

    try:
        logger.info(
            f"Request ID: {request_id} - Fetching feedback summary"
        )

        feedback_manager = FeedbackManager()
        summary = feedback_manager.get_summary()

        logger.info(
            f"Request ID: {request_id} - Feedback summary generated successfully"
        )

        return summary
    
    except Exception as error:
        logger.exception(
            f"Request ID: {request_id} - Error while generating feedback summary"
        )
        raise HTTPException(status_code=500, detail=str(error))

@router.post("/knowledge-base/re-build", response_model = BuildKnowledgeBaseResponse, tags = ['RAG'])
def rebuild_knowledge_base(http_request: Request):
    request_id = http_request.state.request_id

    try:
        logger.info(
            f"Request ID: {request_id} - Rebuilding knowledge base"
        )

        result = build_knowledge_base()
        reload_retriever()

        logger.info(
            f"Request ID: {request_id} - Knowledge base rebuilt successfully with | document {result['total_documents']} | chunks {result['total_chunks']} | file {result['knowledge_file']}"
        )

        return result
    
    except Exception as error:
        logger.exception(
            f"Request ID: {request_id} - Error while rebuilding knowledge base: {str(error)}"
        )
        raise HTTPException(status_code=500, detail=str(error))
    
@router.get("/debug/feedback", tags = ["debug"])
def get_all_feedback(http_request: Request):
    request_id = http_request.state.request_id

    try:
        from app_database import get_connection

        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM feedback")
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "session_id": row[1],
                    "request_id": row[2],
                    "rating": row[3],
                    "comments": row[4],
                    "timestamp": row[5]
                })

        return {
            "total_rows": len(results),
            "data": results
        }

    except Exception as error:
        logger.exception("[request_id=%s] Error fetching debug feedback", request_id)
        raise HTTPException(status_code=500, detail=str(error))

@router.get("/debug/chat-logs", tags=["debug"])
def get_chat_logs(http_request: Request):
    request_id = http_request.state.request_id

    try:
        from app_database import get_connection

        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM chat_logs ORDER BY id DESC")
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "session_id": row[1],
                    "request_id": row[2],
                    "user_input": row[3],
                    "bot_response": row[4],
                    "intent": row[5],
                    "rag_used": bool(row[6])
                })

        return {
            "total_rows": len(results),
            "data": results
        }

    except Exception as error:
        logger.exception("[request_id=%s] Error fetching chat logs", request_id)
        raise HTTPException(status_code=500, detail=str(error))