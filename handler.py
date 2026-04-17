from config import MODEL_NAME
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(
    model = MODEL_NAME,
    temperature = 0.2
)

SYSTEM_PROMPTS = {
    "chat": "You are a helpful assistant. Use previous conversation context when relevant.",
    "summarize": "You summarize text clearly and concisely. Use previous context if the user is referring to earlier text.",
    "email": "You are a professional email writer. If the user is refining a previously written email, use conversation context.",
    "code": "You help debug and explain code clearly. Use previous conversation context if the user is referring to earlier code."
}

RESPONSE_PROMPT = ChatPromptTemplate.from_template(
        "{system_prompt}\n\n"
        "Chat History: \n{chat_history}\n\n"
        "User: {user_input}\n"
        "Assistant: "
)

output_parser = StrOutputParser()

def build_rag_prompt(base_prompt, retrieved_chunks):
    if not retrieved_chunks:
        return base_prompt
    
    context_lines = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_lines.append(
            f"Context {index}:\n"
            f"Title: {chunk['title']}\n"
            f"Content: {chunk['content']}\n"
        )
    
    joined_context = "\n\n".join(context_lines)

    return (
        f"{base_prompt}\n\n"
        f"Use the retrieved context below only if it is clearly relevant to the user's question.\n"
        f"If the context helps, use it to answer more accurately.\n"
        f"If the context is incomplete or not relevant, do not force it into the answer.\n"
        f"Answer normally if the retrieved context does not help.\n"
        f"Explain in your own words and do not copy the context word-for-word unless the user asks for an exact quote.\n\n"
        f"Retrieved Context:\n{joined_context}"
    )
    
def build_history_text(chat_history, use_history=True):
    if not use_history or not chat_history:
        return ""
    history_lines = []
    for message in chat_history:
        history_lines.append(f"{message['role']}: {message['content']}")
    return "\n".join(history_lines)

def generate_response(system_prompt, 
                      user_input, 
                      chat_history, 
                      use_history = True, 
                      retrieved_chunks = None,
                      retry_reason = "",
                      retry_count = 0
                      ):
    final_system_prompt = build_rag_prompt(system_prompt, retrieved_chunks or [])

    if retry_count == 1 and retry_reason.strip():
        final_system_prompt = (
            f"{final_system_prompt}\n\n"
            f"The previous answer was not good enough.\n"
            f"Issue to fix: {retry_reason.strip()}\n"
            f"Answer the user's original request again more accurately.\n"
            f"Strictly fix the issue above."
        )    

    history_text = build_history_text(chat_history, use_history = use_history)

    chain = RESPONSE_PROMPT | llm | output_parser

    bot_response = chain.invoke({
        "system_prompt": final_system_prompt,
        "chat_history": history_text,
        "user_input": user_input
    })
    
    return bot_response

def handle_chat(user_input, chat_history, retrieved_chunks = None, retry_reason = "", retry_count = 0):
    return generate_response(
        SYSTEM_PROMPTS["chat"],
        user_input,
        chat_history,
        use_history = True,
        retrieved_chunks = retrieved_chunks,
        retry_reason = retry_reason,
        retry_count = retry_count 
    )
def handle_email(user_input, chat_history, retrieved_chunks = None, retry_reason = "", retry_count = 0):
    return generate_response(
        SYSTEM_PROMPTS["email"],
        user_input,
        chat_history,
        use_history = True,
        retrieved_chunks = retrieved_chunks,
        retry_reason = retry_reason,
        retry_count = retry_count 
    )
def handle_summarize(user_input, chat_history, retrieved_chunks = None, retry_reason = "", retry_count = 0):
    return generate_response(
        SYSTEM_PROMPTS["summarize"],
        user_input,
        chat_history,   
        use_history = True,
        retrieved_chunks = retrieved_chunks,
        retry_reason = retry_reason,
        retry_count = retry_count 
    )
def handle_code(user_input, chat_history, retrieved_chunks = None, retry_reason = "", retry_count = 0):
    return generate_response(
        SYSTEM_PROMPTS["code"],
        user_input,
        chat_history,   
        use_history = True,
        retrieved_chunks = retrieved_chunks,
        retry_reason = retry_reason,
        retry_count = retry_count 
    )