from fastapi import APIRouter, HTTPException, Request, Form, UploadFile, File
from dependencies import get_memory, build_chat_service, reload_retriever
from feedback_manager import FeedbackManager
from build_knowledge_base import build_knowledge_base
from pdf_ingestion import ingest_pdf_file
import logging
from schemas import (
    ChatRequest, 
    ChatResponse, 
    ResetRequest, 
    ResetResponse, 
    FeedbackRequest, 
    FeedbackSummaryResponse, 
    BuildKnowledgeBaseResponse,
    UploadPDFResponse
)


logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", tags = ["General"])
def home():
    return {"message": "Chatbot API is running"}

@router.get("/health", tags = ["General"])
def health_check():
    return {"status": "ok"}

@router.post("/chat", response_model = ChatResponse, response_model_exclude_none = True, tags = ["Chat"])
def chat(request: ChatRequest, http_request: Request):
    request_id = http_request.state.request_id
    try:
        
        logger.info(
            f"Request ID: {request_id} - endpoint = /chat stage = request_received "
            f"Session: {request.session_id} message_length: {len(request.user_input.strip())} "
            f"use_rag: {request.use_rag} debug: {request.debug}"
        )
        
        memory = get_memory(request.session_id)
        service = build_chat_service(memory)
        
        logger.info(
            f"Request ID: {request_id} - endpoint = /chat stage = service_call_start "
            f"Session: {request.session_id}"
        )

        ChatService_Result = service.process(
            request.user_input, 
            request.session_id,
            request_id,
            use_rag = request.use_rag,
            debug = request.debug
        )

        logger.info(
            f"Request ID: {request_id} - endpoint = /chat stage = service_call_done "
            f"Session: {request.session_id} intent: {ChatService_Result['intent']} "
            f"rag_used: {ChatService_Result['rag_used']} response_length: {len(ChatService_Result['bot_response'])}"
        )
        
        logger.info(
            f"Request ID: {request_id} - endpoint = /chat stage = response_sent "
            f"Session: {request.session_id}"
        )

        return ChatService_Result
    
    except ValueError as ve:
        logger.exception(f"Request ID: {request_id} - endpoint = /chat stage = validation_error")
        raise HTTPException(status_code = 400, detail = str(ve))
    
    except Exception as error:
        logger.exception(f"Request ID: {request_id} - endpoint = /chat stage = unexpected_error")
        raise HTTPException(status_code = 500, detail = str(error))
    
@router.post("/chat-form", response_model = ChatResponse, response_model_exclude_none = True, tags = ["Chat"])
def chat_form(
    http_request: Request,
    user_input: str = Form(...),
    session_id: str = Form(...),
    use_rag: bool = Form(True),
    debug: bool = Form(False)
):
    request_id = http_request.state.request_id

    try:
        logger.info(
            f"Request ID: {request_id} - endpoint = /chat-form stage = request_received "
            f"Session: {session_id} message_length: {len(user_input.strip())} "
            f"use_rag: {use_rag} debug: {debug}"
        )

        memory = get_memory(session_id)
        service = build_chat_service(memory)
        
        logger.info(
            f"Request ID: {request_id} - endpoint = /chat-form stage = service_call_start "
            f"Session: {session_id}"
        )

        ChatService_Result = service.process(
            user_input,
            session_id,
            request_id,
            use_rag = use_rag,
            debug = debug
        )

        logger.info(
            f"Request ID: {request_id} - endpoint = /chat-form stage = service_call_done "
            f"Session: {session_id} intent: {ChatService_Result['intent']} "
            f"rag_used: {ChatService_Result['rag_used']} response_length: {len(ChatService_Result['bot_response'])}"
        )
        
        logger.info(
            f"Request ID: {request_id} - endpoint = /chat-form stage = response_sent "
            f"Session: {session_id}"
        )

        return ChatService_Result

    except ValueError as ve:
        logger.exception(f"Request ID: {request_id} - endpoint = /chat-form stage = validation_error")
        raise HTTPException(status_code = 400, detail = str(ve))
    
    except Exception as error:
        logger.exception(f"Request ID: {request_id} - endpoint = /chat-form stage = unexpected_error")
        raise HTTPException(status_code = 500, detail = str(error))

@router.post("/reset", response_model = ResetResponse, tags = ["Chat"])
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
        raise HTTPException(status_code = 500, detail = str(error))
    
@router.post("/feedback", tags = ["Feedback"])
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
            f"Request ID: {request_id} - Feedback saved successfully for target request: {request.request_id}"
        )

        return {
            "message": "Feedback submitted successfully",
        }
    
    except Exception as error:
        logger.exception(
            f"Request ID: {request_id} - Error while saving feedback"
        )
        raise HTTPException(status_code = 500, detail = str(error))
    
@router.get("/feedback/summary", response_model = FeedbackSummaryResponse, tags = ["Feedback"])
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
        raise HTTPException(status_code = 500, detail = str(error))

@router.post("/knowledge-base/re-build", response_model = BuildKnowledgeBaseResponse, tags = ["RAG"])
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
        raise HTTPException(status_code = 500, detail = str(error))
    
@router.post("/upload-pdf", response_model = UploadPDFResponse, tags = ["Documents"])
async def upload_pdf(file: UploadFile = File(...), http_request: Request = None):
    request_id = http_request.state.request_id

    try:
        logger.info(
            f"Request ID: {request_id} - endpoint = /upload-pdf stage = request_received filename: {file.filename} content_type: {file.content_type}"
        )

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code = 400, detail = "Only PDF files are allowed.")
        
        file.file.seek(0)
        result = ingest_pdf_file(file.file, file.filename)

        logger.info(
            f"Request ID: {request_id} - endpoint = /upload-pdf stage = processing_done filename: {file.filename} total_characters: {result['total_characters']} total_chunks: {result['total_chunks']}"
        )

        return {
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
            "document_id": result["document"]["doc_id"],
            "total_characters": result["total_characters"],
            "total_chunks": result["total_chunks"],
            "chunks": result["chunks"]
        }
    
    except HTTPException:
        raise

    except ValueError as error:
        logger.exception(
            f"Request ID: {request_id} - endpoint = /upload-pdf stage = validation_error"
        )
        raise HTTPException(status_code = 400, detail = str(error))
    
    except Exception as error:
        logger.exception(
            f"Request ID: {request_id} - endpoint = /upload-pdf stage = unexpected_error"
        )
        raise HTTPException(status_code = 500, detail = str(error))

    
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
        logger.exception(f"Request ID: {request_id} - Error fetching debug feedback")
        raise HTTPException(status_code = 500, detail = str(error))

@router.get("/debug/chat-logs", tags = ["debug"])
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
        logger.exception(f"Request ID: {request_id} - Error fetching chat logs")
        raise HTTPException(status_code = 500, detail = str(error)) 