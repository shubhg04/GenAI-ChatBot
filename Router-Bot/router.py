from config import client, MODEL_NAME, classifier_prompt
from handler import handle_chat, handle_email, handle_summarize, handle_code

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
    def __init__(self):
        pass
    def run(self):
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
        intent = classify_intent(user_input)
        print("Intent:", intent)
        bot_response = handlers[intent](user_input)
        print("Bot:", bot_response)
def main():
    bot = ChatBot()
    bot.run()
if __name__ == "__main__":
    main()