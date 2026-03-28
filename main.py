from fastapi import FastAPI, HTTPException
from memory_manager import MemoryManager
from chat_service import ChatService
from schemas import ChatRequest, ChatResponse   

app = FastAPI()
memory = MemoryManager("chat_history.json")
service = ChatService(memory, debug = True)

@app.get("/")
def home():
    return {"message": "Chatbot API is running"} 

@app.post("/chat")
def chat(request: ChatRequest):
      try:
        bot_response = service.process(request.message)
        return bot_response
      except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))
@app.post("/reset")
def reset():
    try:
        memory.clear()
        return {"message": "Chat memory cleared successfully"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))