import logging
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from routing import classify_intent, handlers
from response_evaluator import ResponseEvaluator
from config import RAG_TOP_K

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    user_input: str
    chat_history: list[dict[str, str]]
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

def retrieve_node(state: GraphState) -> GraphState:
    logger.info(
        f"graph_node = retrieve_start use_rag: {state['use_rag']}"
    )
    retrieved_chunks = []
    rag_used = False

    if state["use_rag"]:
        retrieved_chunks = state["retriever"].retrieve(
            state["user_input"],
            top_k = RAG_TOP_K
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
        state["chat_history"],
        retrieved_chunks = state["retrieved_chunks"],
        retry_reason = state.get("evaluation_reason", ""),
        retry_count = state["retry_count"]
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

    evaluation_result = evaluator.evaluate(
        user_input = state["user_input"],
        bot_response = state["bot_response"],
        chat_history = state["chat_history"]
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