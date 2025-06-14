from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pinecone import Pinecone
import redis
import pandas as pd
import json
import uuid
import os

# Load environment
load_dotenv()

# Init clients
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME=os.getenv("PINECONE_INDEX_NAME")
index = pc.Index("INDEX_NAME")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
model = SentenceTransformer('embaas/sentence-transformers-multilingual-e5-base')

# Redis session store
class RedisMemoryStore:
    def __init__(self, session_id: str):
        self.session_id = session_id

    def load(self):
        raw = redis_client.get(self.session_id)
        if raw:
            return json.loads(raw)
        return []

    def save(self, memory: list):
        redis_client.set(self.session_id, json.dumps(memory), ex=3600)  # TTL 1h

    def clear(self):
        redis_client.delete(self.session_id)

# Memory manager
class ChatMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.redis_store = RedisMemoryStore(session_id)
    
    def add_message(self, role: str, message: str):
        history = self.redis_store.load()
        history.append({
            "role": role,
            "message": message,
            "timestamp": pd.Timestamp.now().isoformat()
        })
        self.redis_store.save(history)
    
    def format_history_for_context(self, max_messages: int = 6):
        history = self.redis_store.load()
        recent = history[-max_messages:]
        return "\n".join([f"{'Người dùng' if m['role'] == 'user' else 'Bot'}: {m['message']}" for m in recent])

    def clear_history(self):
        self.redis_store.clear()

# RAG chatbot core

async def rag_qa_chatbot_with_memory(query: str, index, chat_memory: ChatMemory):
    chat_memory.add_message("user", query)

    query_embedding = model.encode(query).tolist()

    results = index.query(vector=query_embedding, top_k=3, include_metadata=True)

    if not results['matches']:
        response = "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn."
        chat_memory.add_message("bot", response)
        return response

    context = "\n".join([match['metadata']['text'] for match in results['matches']])
    conversation_context = chat_memory.format_history_for_context()

    prompt = f"""
Bạn là một trợ lý AI thông minh và hữu ích. Hãy trả lời câu hỏi dựa trên thông tin được cung cấp và lịch sử cuộc trò chuyện.

{conversation_context}

Thông tin tham khảo:
{context}

Câu hỏi hiện tại: {query}

Hướng dẫn:
- Trả lời bằng tiếng Việt
- Dựa trên thông tin được cung cấp và lịch sử trò chuyện
- Nếu câu hỏi liên quan đến cuộc trò chuyện trước đó, hãy tham khảo lịch sử
- Nếu không có thông tin, chỉ cần trả lời "Xin lỗi, hiện tại chúng tôi không thể xử lý yêu cầu này. Bạn có thể thử một yêu cầu khác."
- Trả lời ngắn gọn và dễ hiểu
- Giọng điệu thân thiện, lịch sự
- Sử dụng định dạng markdown nếu cần
- Khi câu hỏi yêu cầu giải thích chi tiết, hãy cố gắng diễn giải dễ hiểu và đầy đủ nhất có thể
- Nếu user hỏi về cuộc trò chuyện trước ("vừa nãy", "câu hỏi trước", etc.), hãy tham khảo lịch sử
"""

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=500,
        )
    )

    bot_response = response.text.strip()
    chat_memory.add_message("bot", bot_response)
    return bot_response

# FastAPI
app = FastAPI()

class ChatRequest(BaseModel):
    query: str
    tenant_id: str = None

def create_session_id(request: Request, tenant_id: str):    
    random_id = uuid.uuid4().hex[:8]
    session_id = f"{tenant_id}-{random_id}"
    return session_id

@app.get("/")
def root():
    return {"message": "API OK"}

@app.post("/chat")
async def chat(request: Request, body: ChatRequest):
    try:
        # Early return cho greeting - không cần RAG
        if any(word in body.query.lower().split() for word in ['hi', 'hello', 'chào', 'xin chào']):
            session_id = request.headers.get("x-session-id") or request.query_params.get("session_id")
            if not session_id and body.tenant_id:
                session_id = create_session_id(request, body.tenant_id)
            return {"response": "Xin chào! Tôi có thể giúp gì cho bạn?", "session_id": session_id}
        
        session_id = request.headers.get("x-session-id") or request.query_params.get("session_id")

        if session_id is None:
            if not body.tenant_id:
                raise HTTPException(status_code=400, detail="Tenant ID is required for new sessions.")
            session_id = create_session_id(request, body.tenant_id)
            
        memory = ChatMemory(session_id)
        response = await rag_qa_chatbot_with_memory(body.query, index, memory) # using await for async function to reduce execution time
        return {"response": response, "session_id": session_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear_session")
async def clear_session(request: Request, tenant_id: str):
    session_id = request.headers.get("x-session-id") or request.query_params.get("session_id")
    memory = ChatMemory(session_id)
    memory.clear_history()
    return {"message": "Session cleared", "session_id": session_id}
