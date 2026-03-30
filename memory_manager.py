import json
import os
class MemoryManager:
    def __init__(self, file_path="chat_history.json"):
        self.file_path = file_path

    def load(self):
        default_history  = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                backup_file = f"{self.file_path}.backup"
                try:
                    os.rename(self.file_path, backup_file)
                    print(f"[DEBUG] Corrupted memory backed up as: {backup_file}")
                except Exception as backup_error:
                    print(f"[DEBUG] Failed to create backup: {backup_error}")

                print("[DEBUG] Failed to load memory. Using default.")      

        return default_history
    
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