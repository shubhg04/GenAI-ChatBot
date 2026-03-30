import json
import os
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, file_path="chat_history.json"):
        self.file_path = file_path
    
    def default_history(self):
        return [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    def load(self):
        default_history  = self.default_history()

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                backup_file = f"{self.file_path}.backup"
                try:
                    os.rename(self.file_path, backup_file)
                    logger.warning(f"Corrupted memory backed up as: {backup_file}")
                except Exception as backup_error:
                    logger.warning(f"Failed to create backup: {backup_error}")

                logger.warning("Failed to load memory. Using default.")

        return default_history
    
    def save(self, chat_history):
        with open(self.file_path, "w") as f:
            json.dump(chat_history, f, indent=2)

    def clear(self):
        default_history  = self.default_history()
        with open(self.file_path, "w") as f:
            json.dump(default_history, f, indent=2)
        return default_history