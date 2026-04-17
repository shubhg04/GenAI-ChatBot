from memory_manager import MemoryManager
from retriever import FAISSRetriever
from langgraph_flow import build_langgraph_flow


def main():
    session_id = "ts-1"
    memory = MemoryManager("chat_history.json")
    retriever = FAISSRetriever()
    graph = build_langgraph_flow()

    initial_state = {
        "user_input": "Who is bobby and where does he live ?",
        "chat_history": memory.load(),
        "use_rag": True,
        "retriever": retriever,
        "intent": "",
        "retrieved_chunks": [],
        "rag_used": False,
        "bot_response": "",
        "evaluation": {},
        "evaluation_reason": "",
        "retry_count": 0
    }

    final_state = graph.invoke(initial_state)

    print("\nLANGGRAPH DEBUG SUMMARY\n")

    print(f"intent: {final_state['intent']}")

    print(f"rag_used: {final_state['rag_used']}")

    print(f"retry_count: {final_state['retry_count']}")

    print(f"retry_happened: {final_state['retry_count'] > 0}")

    print(f"evaluation_score: {final_state['evaluation'].get('score')}")

    print(f"evaluation_reason: {final_state['evaluation'].get('reason')}")

    print(f"retrieved_chunks_count: {len(final_state['retrieved_chunks'])}")

    print("\nFINAL BOT RESPONSE\n")

    print(final_state["bot_response"])

    print("\nFULL RESULT\n")

    result = {
        "user_input": initial_state["user_input"],
        "bot_response": final_state["bot_response"],
        "intent": final_state["intent"],
        "session_id": session_id,
        "rag_used": final_state["rag_used"],
        "retrieved_chunks": final_state["retrieved_chunks"],
        "evaluation": final_state["evaluation"],
        "retry_count": final_state["retry_count"],
        "retry_happened": final_state["retry_count"] > 0
    }

    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()