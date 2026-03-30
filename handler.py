from config import client, MODEL_NAME

def generate_response(system_prompt, user_input, chat_history, use_history=True):
    messages = [{"role": "system", "content": system_prompt}]
    
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

def handle_chat(user_input, chat_history):
    return generate_response(
        "You are a helpful assistant. Use previous conversation context when relevant.",
        user_input,
        chat_history,
        use_history = True
    )
def handle_email(user_input, chat_history):
    return generate_response(
        "You are a professional email writer. If the user is refining a previously written email, use conversation context.",
        user_input,
        chat_history,
        use_history = True
    )
def handle_summarize(user_input, chat_history):
    return generate_response(
        "You summarize text clearly and concisely. Use previous context if the user is referring to earlier text.",
        user_input,
        chat_history,   
        use_history = True
    )
def handle_code(user_input, chat_history):
    return generate_response(
        "You help debug and explain code clearly. Use previous conversation context if the user is referring to earlier code.",
        user_input,
        chat_history,   
        use_history = True
    )