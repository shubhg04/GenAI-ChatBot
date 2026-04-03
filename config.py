from groq import Groq
client = Groq()
MODEL_NAME = "llama-3.1-8b-instant"
classifier_prompt = """
You are an intent classifier for a GenAI assistant.
Your job is to classify the user's message into exactly one of these labels:
chat
summarize
email
code
Rules:
- Return only one label from this list: chat, summarize, email, code
- Do not explain your answer
- Do not write a sentence
- Do not add punctuation
- If the message asks to summarize, shorten, explain briefly, or make something concise, return summarize
- If the message asks to write, draft, compose, send, or reply to an email or message, return email
- If the message asks about code, programming, bugs, debugging, errors, or fixing code, return code
- For anything else, return chat
"""

RAG_KNOWLEDGE_FILE = "knowledge_base.json"
RAG_TOP_K = 3
RAG_MIN_SCORE = 2