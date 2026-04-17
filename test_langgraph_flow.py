from memory_manager import MemoryManager
from retriever import FAISSRetriever
from langgraph_flow import build_langgraph_flow


def main():
    session_id = "ts-1"
    memory = MemoryManager("chat_history.json")
    retriever = FAISSRetriever()
    graph = build_langgraph_flow()

    initial_state = {
        "user_input": "Explain RAG in simple words",
        "chat_history": memory.load(),
        "use_rag": True,
        "retriever": retriever,
        "intent": "",
        "retrieved_chunks": [],
        "rag_used": False,
        "bot_response": "",
        "evaluation": {},
        "retry_count": 0
    }

    final_state = graph.invoke(initial_state)

    result = {
        "user_input": initial_state["user_input"],
        "bot_response": final_state["bot_response"],
        "intent": final_state["intent"],
        "session_id": session_id,
        "rag_used": final_state["rag_used"],
        "retrieved_chunks": final_state["retrieved_chunks"],
        "evaluation": final_state["evaluation"]
    }

    print("\nFINAL GRAPH RESULT\n")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()