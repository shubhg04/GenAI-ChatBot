import logging
from chat_log_repository import ChatLogRepository
from langgraph_flow import build_langgraph_flow
from typing import cast
from langgraph_flow import GraphState

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, memory, user_id, retriever_builder, debug=False):
        self.memory = memory
        self.debug = debug
        self.user_id = user_id
        self.retriever_builder = retriever_builder
        self.chat_log_repository = ChatLogRepository()
        self.graph = build_langgraph_flow()

    def process(self, user_input, session_id, request_id, user_id, use_rag=True, debug=False, selected_doc_ids=None):
        clean_input = user_input.strip()
        if not clean_input:
            raise ValueError("Your input cannot be empty.")

        logger.info(
            f"Request ID: {request_id} flow = start Session: {session_id} "
            f"input_length: {len(clean_input)} use_rag: {use_rag} debug: {debug or self.debug}"
        )

        logger.info(
            f"Request ID: {request_id} flow = graph_start Session: {session_id}"
        )
        
        retriever = self.retriever_builder(user_id, selected_doc_ids)

        initial_state = {
            "user_input": clean_input,
            "session_id": session_id,
            "user_id": user_id,
            "use_rag": use_rag,
            "selected_doc_ids": selected_doc_ids,
            "retriever": retriever,
            "intent": "",
            "retrieved_chunks": [],
            "rag_used": False,
            "bot_response": "",
            "evaluation": {},
            "evaluation_reason": "",
            "retry_count": 0
        }

        final_state = self.graph.invoke(cast(GraphState, initial_state))

        intent = final_state["intent"]
        retrieved_chunks = final_state["retrieved_chunks"]
        rag_used = final_state["rag_used"]
        bot_response = final_state["bot_response"]
        evaluation_result = final_state["evaluation"]
        retry_count = final_state["retry_count"]
        retry_happened = retry_count > 0

        logger.info(
            f"Request ID: {request_id} flow = graph_done Session: {session_id} intent: {intent} rag_used: {rag_used} response_length: {len(bot_response)}"
        )

        logger.info(
            f"Request ID: {request_id} flow = db_save_start Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used}"
        )

        self.chat_log_repository.save_chat_log(
            session_id=session_id,
            request_id=request_id,
            user_input=clean_input,
            bot_response=bot_response,
            intent=intent,
            rag_used=rag_used,
            user_id=user_id
        )

        logger.info(
            f"Request ID: {request_id} flow = db_save_done Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used}"
        )

        logger.info(
            f"Request ID: {request_id} flow = complete Session: {session_id} "
            f"intent: {intent} rag_used: {rag_used} response_length: {len(bot_response)}"
        )

        result = {
            "user_input": clean_input,
            "bot_response": bot_response,
            "intent": intent,
            "session_id": session_id,
            "rag_used": rag_used,
        }

        if debug or self.debug:
            result["retrieved_chunks"] = retrieved_chunks
            result["evaluation"] = evaluation_result
            result["retry_count"] = retry_count
            result["retry_happened"] = retry_happened

        return result