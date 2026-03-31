from memory_manager import MemoryManager
from chat_service import ChatService  
import argparse
import uuid

class ChatBot:
    def __init__(self, debug = False):
        self.memory = MemoryManager("chat_history.json")
        self.debug = debug
        self.service = ChatService(self.memory, debug = self.debug)
    
    def run(self):
        while True:
            user_input = input("User: ")
            if self.debug:
                print("[Debug] User Input:", user_input) 
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            if user_input.lower() == "reset":
                self.memory.clear()
                print("Bot: Memory cleared.")
                continue
            
            request_id = str(uuid.uuid4())
            ChatService_Result = self.service.process(user_input, "cli-session" , request_id)

            print("Bot:", ChatService_Result["bot_response"])
            if not self.debug:
                print("Intent:", ChatService_Result["intent"])

def main(debug = False):
    bot = ChatBot(debug)
    if debug:
        print("Debug mode is ON")
    bot.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    main(debug=args.debug)