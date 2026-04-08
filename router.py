from memory_manager import MemoryManager
from chat_service import ChatService  
from retriever import FAISSRetriever
import argparse
import uuid

retriever = FAISSRetriever()

def read_multiline_input():
    print("User (type DONE on a new line to finish):")
    lines = []

    while True:
        line = input()
        if line.strip() == "DONE":
            break
        lines.append(line)

    return "\n".join(lines).strip()

class ChatBot:
    def __init__(self, debug = False):
        self.memory = MemoryManager("chat_history.json")
        self.debug = debug
        self.service = ChatService(self.memory, retriever = retriever, debug = self.debug)
    
    def run(self):
        while True:
            user_input = read_multiline_input()
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