import os
from memory_manager import MemoryManager
from chat_service import ChatService

debug_mode = True

memory_dir = "memory_files"

def get_memory(session_id: str):
    os.makedirs(memory_dir, exist_ok=True)
    file_path = os.path.join(memory_dir, f"{session_id}.json")
    return MemoryManager(file_path)

def build_chat_service(memory):
    return ChatService(memory, debug = debug_mode)