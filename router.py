from config import client, MODEL_NAME, classifier_prompt
from handler import handle_chat, handle_email, handle_summarize, handle_code
from memory_manager import MemoryManager
import argparse
def classify_intent(user_input):
    response = client.chat.completions.create(
        model = MODEL_NAME,
        messages=[
            {"role": "system", "content": classifier_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature = 0
    )
    raw = response.choices[0].message.content.strip().lower()
    intent = raw.split()[0]
    if intent not in ["chat", "summarize", "email", "code"]:
        intent = "chat"
    return intent

handlers = {
    "chat": handle_chat,
    "summarize": handle_summarize,
    "email": handle_email,
    "code": handle_code
}
class ChatBot:
    def __init__(self, debug = False):
        self.memory = MemoryManager("chat_history.json")
        self.chat_history = self.memory.load()
        self.debug = debug
    def run(self):
        while True:
            user_input = input("User: ")
            if self.debug:
                print("[Debug] User Input:", user_input) 
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            if user_input.lower() == "reset":
                self.chat_history = self.memory.clear()
                print("Bot: Memory cleared.")
                continue
            intent = classify_intent(user_input)
            if self.debug:
                print("[Debug] Inten:", intent)  
                print("[Debug] Handler:", handlers[intent].__name__)
            bot_response = handlers[intent](user_input, self.chat_history)
            print("Bot:", bot_response)
            self.memory.save(self.chat_history)
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