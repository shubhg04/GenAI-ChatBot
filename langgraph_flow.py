import logging
from uuid import UUID
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from routing import classify_intent, handlers
from response_evaluator import ResponseEvaluator
from langchain_memory_adapter import LangChainMemoryAdapter
from config import RAG_TOP_K
import re

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    user_input: str
    session_id: str
    user_id: UUID
    use_rag: bool
    retriever: Any
    intent: str
    retrieved_chunks: list[dict[str, Any]]
    rag_used: bool
    bot_response: str
    evaluation: dict[str, str]
    evaluation_reason: str
    retry_count: int

def classify_node(state: GraphState) -> GraphState:
    logger.info(
        f"graph_node = classify_start input_length: {len(state['user_input'])}"
    )
    intent = classify_intent(state["user_input"])
    state["intent"] = intent

    logger.info(
        f"graph_node = classify_done intent: {intent} "
    )
    return state

def build_retrieval_query(user_input: str) -> str:
    cleaned_input = user_input.strip().lower()

    filler_patterns = [
        r"\bhi\b",
        r"\bhello\b",
        r"\bhey\b",
        r"\bplease\b",
        r"\bthanks\b",
        r"\bthank you\b",
        r"\bcan you tell me\b",
        r"\bcould you tell me\b",
        r"\btell me\b"
    ]

    for pattern in filler_patterns:
        cleaned_input = re.sub(pattern, " ", cleaned_input)

    cleaned_input = re.sub(r"\s+", " ", cleaned_input).strip()

    return cleaned_input or user_input.strip()

def retrieve_node(state: GraphState) -> GraphState:
    logger.info(
        f"graph_node = retrieve_start use_rag: {state['use_rag']}"
    )
    retrieved_chunks = []
    rag_used = False

    if state["use_rag"]:
        retrieval_query = build_retrieval_query(state["user_input"])

        logger.info(
            f"graph_node = retrieve_query_built original_input: {state['user_input']} retrieval_query: {retrieval_query}"
        )

        retrieved_chunks = state["retriever"].retrieve(
            retrieval_query,
            top_k=RAG_TOP_K
        )

        rag_used = len(retrieved_chunks) > 0

    state["retrieved_chunks"] = retrieved_chunks
    state["rag_used"] = rag_used

    logger.info(
        f"graph_node = retrieve_done rag_used: {rag_used} retrieved_count: {len(retrieved_chunks)} "
    )
    return state

def generate_node(state: GraphState) -> GraphState:
    logger.info(
        f"graph_node = generate_start intent: {state['intent']} rag_used: {state['rag_used']} retry_count: {state['retry_count']}"
    )
    intent = state["intent"]
    handler = handlers.get(intent, handlers["chat"])

    bot_response = handler(
        state["user_input"],
        state["session_id"],
        state["user_id"],
        retrieved_chunks=state["retrieved_chunks"],
        retry_reason=state.get("evaluation_reason", ""),
        retry_count=state["retry_count"]
    )

    state["bot_response"] = bot_response

    logger.info(
        f"graph_node = generate_done response_length: {len(bot_response)} retry_count: {state['retry_count']}"
    )
    return state

def evaluate_node(state: GraphState) -> GraphState:
    logger.info(
        f"graph_node = evaluate_start retry_count: {state['retry_count']}"
    )
    evaluator = ResponseEvaluator()

    adapter = LangChainMemoryAdapter(
        session_id=state["session_id"],
        user_id=state["user_id"]
    )
    history_messages = adapter.messages

    chat_history_for_eval = []
    for message in history_messages:
        role_map = {"system": "system", "human": "user", "ai": "assistant"}
        message_type = message.type
        role = role_map.get(message_type, "user")
        chat_history_for_eval.append({"role": role, "content": message.content})

    evaluation_result = evaluator.evaluate(
        user_input=state["user_input"],
        bot_response=state["bot_response"],
        chat_history=chat_history_for_eval
    )

    state["evaluation"] = evaluation_result
    state["evaluation_reason"] = evaluation_result.get("reason", "").strip()

    logger.info(
        f"graph_node = evaluate_done score: {evaluation_result['score']} reason: {state['evaluation_reason']} retry_count: {state['retry_count']}"
    )
    return state

def prepare_retry_node(state: GraphState) -> GraphState:
    state["retry_count"] += 1

    logger.info(
        f"graph_node = prepare_retry retry_count: {state['retry_count']} reason: {state.get('evaluation_reason', '')}"
    )
    return state

def route_after_evaluation(state: GraphState) -> str:
    score = state["evaluation"].get("score", "incorrect")

    if score == "correct":
        logger.info(
            f"graph_route = finish reason = score_correct retry_count: {state['retry_count']}"
        )
        return "end"

    if state["retry_count"] >= 1:
        logger.info(
            f"graph_route = finish reason = retry_limit_reached score: {score} retry_count: {state['retry_count']}"
        )
        return "end"

    logger.info(
        f"graph_route = retry score: {score} retry_count: {state['retry_count']}"
    )
    return "prepare_retry"

def build_langgraph_flow():
    graph_builder = StateGraph(GraphState)

    graph_builder.add_node("classify", classify_node)
    graph_builder.add_node("retrieve", retrieve_node)
    graph_builder.add_node("generate", generate_node)
    graph_builder.add_node("evaluate", evaluate_node)
    graph_builder.add_node("prepare_retry", prepare_retry_node)

    graph_builder.set_entry_point("classify")

    graph_builder.add_edge("classify", "retrieve")
    graph_builder.add_edge("retrieve", "generate")
    graph_builder.add_edge("generate", "evaluate")
    graph_builder.add_edge("prepare_retry", "generate")
    graph_builder.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "prepare_retry": "prepare_retry",
            "end": END
        }
    )
    return graph_builder.compile()