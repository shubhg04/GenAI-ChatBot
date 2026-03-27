from routing import classify_intent, handlers

class ChatService:
    def __init__(self, memory, debug=False):
        self.memory = memory
        self.debug = debug

    def process(self, user_input):
        chat_history = self.memory.load()
        intent = classify_intent(user_input)
        if self.debug:
            print("[DEBUG] Intent:", intent)
        
        handler = handlers.get(intent)
        if not handler:
            handler = handlers["chat"]
        if self.debug:    
            print("[DEBUG] Handler:", handler.__name__)
        
        bot_response = handler(user_input, chat_history)
        self.memory.save(chat_history)
        return bot_response
