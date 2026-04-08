import logging
from routing import classify_intent, handlers
from config import RAG_TOP_K
from chat_log_repository import ChatLogRepository

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, memory, retriever, debug = False):
        self.memory = memory
        self.debug = debug
        self.retriever = retriever
        self.chat_log_repository = ChatLogRepository()

    def process(self, user_input, session_id, request_id, use_rag = True, debug = False):
        clean_input = user_input.strip()
        if not clean_input:
            raise ValueError("Your input cannot be empty.")

        logger.info(
            f"Request ID: {request_id} flow = start Session: {session_id} "
            f"input_length: {len(clean_input)} use_rag: {use_rag} debug: {debug or self.debug}"
        )

        logger.info(
            f"Request ID: {request_id} flow = memory_load_start Session: {session_id}"
        )

        chat_history = self.memory.load()

        logger.info(
            f"Request ID: {request_id} flow = memory_load_done Session: {session_id}, "
            f"history_messages: {len(chat_history)}"
        )

        logger.info(
            f"Request ID: {request_id} flow = classify_start Session: {session_id}"
        )

        intent = classify_intent(clean_input)

        logger.info(
            f"Request ID: {request_id} flow = classify_done Session: {session_id} intent: {intent}"
        )

        retrieved_chunks = []
        rag_used = False

        if use_rag:
            logger.info(
                f"Request ID: {request_id} flow = retrieve_start Session: {session_id} top_k: {RAG_TOP_K}"
            )

            retrieved_chunks = self.retriever.retrieve(clean_input, top_k = RAG_TOP_K)
            rag_used = len(retrieved_chunks) > 0

            if rag_used:
                top_chunk_summary = ", ".join(
                    f"{chunk['id']} : {chunk['score']}"
                    for chunk in retrieved_chunks[:3]
                )

                logger.info(
                    f"Request ID: {request_id} flow = retrieve_done Session: {session_id} "
                    f"rag_used: {rag_used} retrieved_count: {len(retrieved_chunks)} "
                    f"top_chunks: {top_chunk_summary}"
                )
            else:
                logger.info(
                    f"Request ID: {request_id} flow = retrieve_done Session: {session_id} "
                    f"rag_used: {rag_used} retrieved_count: 0"
                )
        else:
            logger.info(
                f"Request ID: {request_id} flow = retrieve_skipped Session: {session_id} "
                f"rag_used: {rag_used} reason: rag_disabled"
            )

        handler = handlers.get(intent, handlers["chat"])

        logger.info(
            f"Request ID: {request_id} flow = response_start Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used}"
        )

        bot_response = handler(clean_input, chat_history, retrieved_chunks=retrieved_chunks)

        logger.info(
            f"Request ID: {request_id} flow = response_done Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used} response_length: {len(bot_response)}"
        )

        logger.info(
            f"Request ID: {request_id} flow = memory_save_start Session: {session_id}"
        )

        self.memory.save(chat_history)

        logger.info(
            f"Request ID: {request_id} flow = memory_save_done Session: {session_id} "
            f"history_messages: {len(chat_history)}"
        )

        logger.info(
            f"Request ID: {request_id} flow = db_save_start Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used}"
        )

        self.chat_log_repository.save_chat_log(
            session_id = session_id,
            request_id = request_id,
            user_input = user_input,
            bot_response = bot_response,
            intent = intent,
            rag_used = rag_used
        )

        logger.info(
            f"Request ID: {request_id} flow = db_save_done Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used}"
        )

        logger.info(
            f"Request ID: {request_id} flow = complete Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used} response_length: {len(bot_response)}"
        )

        ChatService_result = {
            "user_input": clean_input,
            "bot_response": bot_response,
            "intent": intent,
            "session_id": session_id,
            "rag_used": rag_used,
        }

        if debug or self.debug:
            ChatService_result["retrieved_chunks"] = retrieved_chunks

        return ChatService_result