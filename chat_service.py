import logging
from routing import classify_intent, handlers

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, memory, debug=False):
        self.memory = memory
        self.debug = debug

    def process(self, user_input, session_id, request_id):
        clean_input = user_input.strip() 
        if not clean_input:
            raise ValueError("You input cannot be empty.")

        chat_history = self.memory.load()

        intent = classify_intent(clean_input)
        logger.info(f"Request ID: {request_id} - Session: {session_id} - Classified intent: {intent}")
        
        handler = handlers.get(intent, handlers["chat"])
        #if not handler:
        #    handler = handlers["chat"]

        bot_response = handler(clean_input, chat_history)
        self.memory.save(chat_history)

        logger.info(f"Request ID: {request_id} - Session: {session_id} - Response generated successfully")

        return {
            "user_input":  clean_input,
            "bot_response": bot_response,
            "intent": intent,
            "session_id": session_id
        }
