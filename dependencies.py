from memory_manager import MemoryManager
from chat_service import ChatService

memory = MemoryManager("chat_history.json")
service = ChatService(memory, debug = True)