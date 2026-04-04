import logging
from routing import classify_intent, handlers
from retriever import SimpleRetriever
from config import RAG_TOP_K

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, memory, debug = False):
        self.memory = memory
        self.debug = debug
        self.retriever = SimpleRetriever()

    def process(self, user_input, session_id, request_id, use_rag = True, debug = False):
        clean_input = user_input.strip() 
        if not clean_input:
            raise ValueError("You input cannot be empty.")

        chat_history = self.memory.load()

        intent = classify_intent(clean_input)
        logger.info(f"Request ID: {request_id} - Session: {session_id} - Classified intent: {intent}")
        
        retrieved_chunks = []
        rag_used = False

        if use_rag:
            retrieved_chunks = self.retriever.retrieve(clean_input, top_k = RAG_TOP_K)
            rag_used = len(retrieved_chunks) > 0
            logger.info(
                f"Request ID: {request_id} - Session: {session_id} - vector retrieval returned {len(retrieved_chunks)} chunks"
            )
        else:
            logger.info(
                f"Request ID: {request_id} - Session: {session_id} - RAG disabled for this chat"
            )
            
        handler = handlers.get(intent, handlers["chat"])
        #if not handler:
        #    handler = handlers["chat"]

        bot_response = handler(clean_input, chat_history, retrieved_chunks = retrieved_chunks)
        self.memory.save(chat_history)

        logger.info(f"Request ID: {request_id} - Session: {session_id} - Response generated successfully")
        
        ChatService_Result = {
                "user_input":  clean_input,
                "bot_response": bot_response,
                "intent": intent,
                "session_id": session_id,
                "rag_used": rag_used,
            }

        if debug or self.debug:
            ChatService_Result["retrieved_chunks"] = retrieved_chunks

        return ChatService_Result
            
