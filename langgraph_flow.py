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

def classify_node(state: GraphState) -> GraphState:
    logger.info(
        f"graph_node = classify_start input_length: {len(state['user_input'])} "
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
        f"graph_node = generate_start intent: {state['intent']} rag_used: {state['rag_used']}"
    )
    intent = state["intent"]
    handler = handlers.get(intent, handlers["chat"])

    bot_response = handler(
        state["user_input"],
        state["chat_history"],
        retrieved_chunks = state["retrieved_chunks"]
    )

    state["bot_response"] = bot_response

    logger.info(
        f"graph_node = generate_done response_length: {len(bot_response)}"
    )
    return state

def evaluate_node(state: GraphState) -> GraphState:
    logger.info(
        "graph_node = evaluate_start"
    )
    evaluator = ResponseEvaluator()

    evaluation_result = evaluator.evaluate(
        user_input = state["user_input"],
        bot_response = state["bot_response"]
    )

    state["evaluation"] = evaluation_result
    
    logger.info(
        f"graph_node = evaluate_done score: {evaluation_result['score']} reason: {evaluation_result['reason']}"
    )
    return state

def build_langgraph_flow():
    graph_builder = StateGraph(GraphState)

    graph_builder.add_node("classify", classify_node)
    graph_builder.add_node("retrieve", retrieve_node)
    graph_builder.add_node("generate", generate_node)
    graph_builder.add_node("evaluate", evaluate_node)

    graph_builder.set_entry_point("classify")

    graph_builder.add_edge("classify", "retrieve")
    graph_builder.add_edge("retrieve", "generate")
    graph_builder.add_edge("generate", "evaluate")
    graph_builder.add_edge("evaluate", END)

    return graph_builder.compile()