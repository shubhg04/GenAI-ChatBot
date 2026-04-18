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

        logger.info(f"memory_stage = load_start file_path: {self.file_path}")
        if os.path.exists(self.file_path):
            logger.info(f"memory_stage = file_found file_path:{self.file_path}")
            
            try:
                with open(self.file_path, "r") as f:
                    chat_history = json.load(f)                
                logger.info(
                    f"memory_stage = load_done file_path: {self.file_path} "
                    f"message_count: {len(chat_history)}"
                )
                return chat_history
            
            except Exception as error:
                backup_file = f"{self.file_path}.backup"
                logger.warning(
                    f"memory_stage = load_failed file_path: {self.file_path} error: {str(error)}"
                )
                
                try:
                    os.rename(self.file_path, backup_file)
                    logger.warning(
                        f"memory_stage = backup_created original_file: {self.file_path} "
                        f"backup_file: {backup_file}"
                    )
                
                except Exception as backup_error:
                    logger.warning(
                        f"memory_stage = backup_failed original_file: {self.file_path} "
                        f"backup_file: {backup_file} error: {str(backup_error)}"
                    )
                
                logger.warning(
                    f"memory_stage = load_fallback_default file_path: {self.file_path} "
                    f"default_message_count: {len(default_history)}"
                )
                return default_history
        
        logger.warning(
                    f"memory_stage = load_fallback_default file_path: {self.file_path} "
                    f"default_message_count: {len(default_history)}"
                )
        return default_history
    
    def save(self, chat_history):
        logger.info(
            f"memory_stage = save_start file_path: {self.file_path} "
            f"message_count: {len(chat_history)}"
        )
        
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        with open(self.file_path, "w", encoding = "utf-8") as f:
            json.dump(chat_history, f, indent=2)
        
        logger.info(
            f"memory_stage = save_done file_path: {self.file_path} "
            f"message_count: {len(chat_history)}"
        )
    
    def clear(self):
        default_history  = self.default_history()
        
        logger.info(f"memory_stage = clear_start file_path: {self.file_path}")
        with open(self.file_path, "w") as f:
            json.dump(default_history, f, indent=2)
        
        logger.info(
            f"memory_stage = clear_done file_path: {self.file_path} "
            f"message_count: {len(default_history)}"
        )
        return default_history