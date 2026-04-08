import os
from memory_manager import MemoryManager
from chat_service import ChatService
from retriever import FAISSRetriever
import logging

debug_mode = False
memory_dir = "memory_files"

logger = logging.getLogger(__name__)

_retriever = None

def get_memory(session_id: str):
    os.makedirs(memory_dir, exist_ok = True)
    file_path = os.path.join(memory_dir, f"{session_id}.json")
    
    return MemoryManager(file_path)

def initialize_retriever():
    global _retriever
    
    if _retriever is None:
        logger.info("Initializing shared FAISS retriever...")
        _retriever = FAISSRetriever()
        
        logger.info("Shared FAISS retriever initialized successfully.")
    return _retriever

def get_retriever():
    if _retriever is None:
        raise RuntimeError("Retriever has not been initialized.")
    return _retriever

def reload_retriever():
    global _retriever
    
    logger.info("Reloading shared FAISS retriever...")
    _retriever = FAISSRetriever()
    
    logger.info("Shared FAISS retriever reloaded successfully.")
    return _retriever 

def build_chat_service(memory):
    return ChatService(memory, retriever = get_retriever(), debug = debug_mode)