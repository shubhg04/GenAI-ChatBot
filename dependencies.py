from memory_manager import MemoryManager
from chat_service import ChatService

debug_mode = True

def get_memory():
    return MemoryManager("chat_history.json")

def build_chat_service(memory: MemoryManager):
    return ChatService(memory, debug = debug_mode)