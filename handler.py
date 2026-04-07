from config import client, MODEL_NAME

def build_rag_prompt(base_prompt, retrieved_chunks):
    if not retrieved_chunks:
        return base_prompt
    
    context_lines = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_lines.append(
            f"Context {index}:\nTitle: {chunk['title']}\nContent: {chunk['content']}\n"
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

def generate_response(system_prompt, user_input, chat_history, use_history=True, retrieved_chunks = None):
    final_system_prompt = build_rag_prompt(system_prompt, retrieved_chunks or [])

    messages = [{"role": "system", "content": final_system_prompt}]
    
    if use_history:
        messages += chat_history[-10:]
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model = MODEL_NAME,
        messages = messages,
        temperature = 0.2
    )
    
    bot_response = response.choices[0].message.content.strip()
    
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": bot_response})
    
    if len(chat_history) > 21:
        chat_history[:] = [chat_history[0]] + chat_history[-20:]
    return bot_response

def handle_chat(user_input, chat_history, retrieved_chunks = None):
    return generate_response(
        "You are a helpful assistant. Use previous conversation context when relevant.",
        user_input,
        chat_history,
        use_history = True,
        retrieved_chunks = retrieved_chunks
    )
def handle_email(user_input, chat_history, retrieved_chunks = None):
    return generate_response(
        "You are a professional email writer. If the user is refining a previously written email, use conversation context.",
        user_input,
        chat_history,
        use_history = True,
        retrieved_chunks = retrieved_chunks
    )
def handle_summarize(user_input, chat_history, retrieved_chunks = None):
    return generate_response(
        "You summarize text clearly and concisely. Use previous context if the user is referring to earlier text.",
        user_input,
        chat_history,   
        use_history = True,
        retrieved_chunks = retrieved_chunks
    )
def handle_code(user_input, chat_history, retrieved_chunks = None):
    return generate_response(
        "You help debug and explain code clearly. Use previous conversation context if the user is referring to earlier code.",
        user_input,
        chat_history,   
        use_history = True,
        retrieved_chunks = retrieved_chunks
    )