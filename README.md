# Smart RAG Assistant

An intelligent chatbot system using RAG (Retrieval-Augmented Generation) technology to answer questions based on knowledge stored in a vector database. The system supports session management and contextual memory to create natural conversational experiences.

## 🚀 Key Features

- **RAG (Retrieval-Augmented Generation)**: Search relevant information and generate answers based on knowledge base
- **Session Management**: Store conversation history with Redis
- **Contextual Memory**: Chatbot remembers previous conversation context
- **Multilingual Support**: Optimized for Vietnamese language
- **RESTful API**: Simple and easy-to-integrate API interface
- **Docker Support**: Easy deployment with Docker

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI**: Modern, fast, and easy-to-use web framework
- **Python 3.11**: Primary programming language

### AI/ML Components
- **Google Gemini 2.0 Flash**: Large Language Model for answer generation
- **Sentence Transformers**: Embedding model for text vectorization
  - Model: `embaas/sentence-transformers-multilingual-e5-base`
- **Pinecone**: Vector database for storing and searching embeddings

### Database & Cache
- **Redis**: Store chatbot sessions and memory
- **Pinecone**: Vector database for RAG

### Deployment
- **Docker**: Application containerization
- **Uvicorn**: ASGI server for FastAPI

## 📋 System Requirements

- Python 3.11+
- Redis server
- Google AI account (Gemini API)
- Pinecone account

## 🚀 Installation Guide

### 1. Clone repository

```bash
git clone <repository-url>
cd smart-rag-assistant
```

### 2. Create Python virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
# Google AI API
GOOGLE_API_KEY=your_google_api_key_here

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=your_index_name_here

# Redis
REDIS_URL=your_redis_url
```

### 5. Prepare data

Make sure you have:
- Created Pinecone index with dimensions matching the embedding model
- Uploaded data to Pinecone index
- Started Redis server

### 6. Run the application

#### Development mode:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port <your-port>
```

#### Production mode:
```bash
uvicorn app:app --host 0.0.0.0 --port <your-port>
```

### 7. Run with Docker

```bash
# Build image
docker build -t smart-rag-assistant .

# Run container
docker run -d \
  --name smart-rag-assistant \
  -p <your-port>:<your-port>\
  --env-file .env \
  smart-rag-assistant
```

## 📚 API Documentation

### Base URL
```
http://localhost:<your-port>
```

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "API OK"
}
```

#### 2. Chat
```http
POST /chat
```

**Request Body:**
```json
{
  "query": "Your question here",
  "tenant_id": "your_tenant_id"
}
```

**Headers (optional):**
```
x-session-id: your_session_id
```

**Response:**
```json
{
  "response": "Chatbot's answer",
  "session_id": "generated_or_existing_session_id"
}
```

#### 3. Clear Session
```http
POST /clear_session?tenant_id=your_tenant_id
```

**Headers:**
```
x-session-id: your_session_id
```

**Response:**
```json
{
  "message": "Session cleared",
  "session_id": "your_session_id"
}
```

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/UI     │    │   FastAPI App   │    │   Google AI     │
│                 │───▶│                 │───▶│   (Gemini)      │
└─────────────────┘    │   - Routing     │    └─────────────────┘
                       │   - Validation  │
                       │   - Session Mgmt│    ┌─────────────────┐
                       └─────────────────┘───▶│   Pinecone      │
                                │              │   (Vector DB)   │
                                │              └─────────────────┘
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │ Sentence Trans. │
                       │   - Sessions    │    │   - Embeddings  │
                       │   - Memory      │    └─────────────────┘
                       └─────────────────┘
```

## 🔧 Customization

### Change Embedding Model
Modify in `app.py`:
```python
model = SentenceTransformer('your-preferred-model')
```

### Adjust RAG Parameters
```python
# In rag_qa_chatbot_with_memory function
results = index.query(
    vector=query_embedding,
    top_k=3,  # Number of documents to return
    include_metadata=True
)
```

### Configure Memory
```python
# Number of messages to keep in memory
def format_history_for_context(self, max_messages: int = 6):
```

## 🙏 Acknowledgments

- Google AI team for Gemini API
- Pinecone team for vector database
- Sentence Transformers community
- FastAPI and Redis communities

## 🚧 Development Status

This project is currently in active development. I am continuously working to improve the system and add new capabilities.

### 🔮 Upcoming Features

- **Large-scale Data Q&A**: Enhanced support for querying and analyzing massive datasets with improved performance and accuracy
- **Voice Communication**: Audio input/output capabilities for natural voice conversations with the chatbot
- **Action Execution**: Ability to perform specific actions based on user requests, including:
  - File operations
  - API integrations
  - System commands
  - Database operations
- **Advanced RAG Techniques**: Implementation of more sophisticated retrieval methods
- **Multi-modal Support**: Integration of text, image, and document processing
- **Enhanced Memory Management**: Long-term conversation memory with better context retention

### 📊 Current Limitations

- Text-only interactions
- Limited to predefined knowledge base
- Session memory has 1-hour TTL
- Vietnamese language optimization (expanding to other languages)

Stay tuned for updates and new releases! 🚀