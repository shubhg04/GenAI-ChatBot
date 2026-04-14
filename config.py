from groq import Groq

client = Groq()

MODEL_NAME = "llama-3.1-8b-instant"
EVALUATOR_MODEL_NAME = "llama-3.1-8b-instant"

RAG_KNOWLEDGE_FILE = "knowledge_base.json"
RAG_METADATA_FILE = "knowledge_metadata.json"
FAISS_INDEX_FILE = "knowledge.index"
RAG_TOP_K = 3
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RAG_SIMILARITY_THRESHOLD = 0.3

classifier_prompt = """
You are a strict intent classifier.

Classify the user's message into exactly one of these labels only:
chat
summarize
email
code

Rules:
- Allowed outputs are only: chat, summarize, email, code
- Return only one label
- Do not explain
- Do not add punctuation
- Do not add extra words
- Do not add new lines

Classification rules:
- If the user asks to summarize, shorten, condense, or explain briefly, output summarize
- If the user asks to write, draft, compose, send, or reply to an email or message, output email
- Output code only when the user is asking to write code, fix code, debug code, explain code, analyze an error, or help with programming syntax or implementation
- If the user is asking about a technical concept in simple words, theory, meaning, definition, comparison, or explanation, output chat
- If the message is general conversation, explanation, or knowledge question, output chat
- When unsure, output chat
"""

evaluation_prompt = """
You are a strict response evaluator.

You will be given:
1. User input
2. Bot response

Your job is to judge whether the bot response correctly answers the user.

Return output in exactly this format only:

score: correct
reason: <short reason>

OR

score: partially_correct
reason: <short reason>

OR

score: incorrect
reason: <short reason>

Rules:
- Allowed scores are only: correct, partially_correct, incorrect
- Keep the reason short, specific, and practical
- Judge the bot response only against the user's actual request
- Do not invent issues that are not clearly present
- If the response misses the main point, say what main point was missed
- If the response is partly right but misses an important detail, use partially_correct
- If the response answers a different question than what the user asked, use incorrect
- Do not add extra text
"""


