import json
import os
class MemoryManager:
    def __init__(self, file_path="chat_history.json"):
        self.file_path = file_path

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                print("[DEBUG] Failed to load memory. Using default.")               
        return [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    def save(self, chat_history):
        with open(self.file_path, "w") as f:
            json.dump(chat_history, f, indent=2)

    def clear(self):
        default_history  = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        with open(self.file_path, "w") as f:
            json.dump(default_history, f, indent=2)
        return default_history