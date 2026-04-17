import logging
from chat_log_repository import ChatLogRepository
from langgraph_flow import build_langgraph_flow

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, memory, retriever, debug = False):
        self.memory = memory
        self.debug = debug
        self.retriever = retriever
        self.chat_log_repository = ChatLogRepository()
        self.graph = build_langgraph_flow()

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
            f"Request ID: {request_id} flow = graph_start Session: {session_id}"
        )

        initial_state = {
            "user_input": clean_input,
            "chat_history": chat_history,
            "use_rag": use_rag,
            "retriever": self.retriever,
            "intent": "",
            "retrieved_chunks": [],
            "rag_used": False,
            "bot_response": "",
            "evaluation": {},
            "retry_count": 0
        }

        final_state = self.graph.invoke(initial_state)

        intent = final_state["intent"]
        retrieved_chunks = final_state["retrieved_chunks"]
        rag_used = final_state["rag_used"]
        bot_response = final_state["bot_response"]
        evaluation_result = final_state["evaluation"]

        logger.info(
            f"Request ID: {request_id} flow = graph_done Session: {session_id} intent: {intent} rag_used: {rag_used} response_length: {len(bot_response)}"
        )

        logger.info(
            f"Request ID: {request_id} flow = memory_update_start Session: {session_id}"
        )

        save_to_memory = True

        if save_to_memory:
            chat_history.append({"role": "user", "content": clean_input})
            chat_history.append({"role": "assistant", "content": bot_response})

            if len(chat_history) > 21:
                chat_history[:] = [chat_history[0]] + chat_history[-20:]   

            logger.info(
                f"Request ID: {request_id} flow = memory_update_done Session: {session_id} "
                f"history_messages: {len(chat_history)}"
            ) 

            logger.info(
                f"Request ID: {request_id} flow = memory_save_start Session: {session_id}"
            )        

            self.memory.save(chat_history)

            logger.info(
                f"Request ID: {request_id} flow = memory_save_done Session: {session_id} "
                f"history_messages: {len(chat_history)}"
            )

        else:
            logger.info(
                f"Request ID: {request_id} memory_save_skipped Session: {session_id}"
            )

        logger.info(
            f"Request ID: {request_id} flow = db_save_start Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used}"
        )

        self.chat_log_repository.save_chat_log(
            session_id = session_id,
            request_id = request_id,
            user_input = clean_input,
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
            ChatService_result["evaluation"] = evaluation_result

        return ChatService_result