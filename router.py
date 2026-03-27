from config import client, MODEL_NAME, classifier_prompt
from handler import handle_chat, handle_email, handle_summarize, handle_code
import argparse
import json
import os
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
        self.history_file = "chat_history.json"
        self.chat_history = self.load_chat_history()
        self.debug = debug
    def load_chat_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception:
                print("[DEBUG] Failed to load chat history. Using default.")
        return [{"role": "system", "content": "You are a helpful assistant."}]
    def save_chat_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.chat_history, f, indent = 2)
    def run(self):
        while True:
            user_input = input("User: ")
            if self.debug:
                print("[Debug] User Input:", user_input) 
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            intent = classify_intent(user_input)
            if self.debug:
                print("[Debug] Inten:", intent)  
                print("[Debug] Handler:", handlers[intent].__name__)
            bot_response = handlers[intent](user_input, self.chat_history)
            print("Bot:", bot_response)
            self.save_chat_history()
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