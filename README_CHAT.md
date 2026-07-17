# Chat App with Async Evaluation

Streamlit chat interface with ChatGPT + FastAPI backend for async Vertex AI evaluation.

## Architecture

```
User → Streamlit Chat → OpenAI ChatGPT
                ↓
         FastAPI Backend → Vertex AI Evaluation (async)
                ↓
         Results stored in memory
```

## Setup

```bash
# Install dependencies
pip install -r requirements_chat.txt

# Configure environment
cp .env.example .env
# Add OPENAI_API_KEY and GCP_PROJECT_ID

# Start both services
./start.sh
```

## Manual Start

```bash
# Terminal 1: FastAPI
uvicorn eval_api:app --reload --port 8000

# Terminal 2: Streamlit
streamlit run chat_app.py
```

## Features

### Chat Interface
- Real-time chat with ChatGPT
- Message history
- Clean UI

### Async Evaluation
- Evaluates each response in background
- Metrics: coherence, fluency, quality (1-5)
- Non-blocking evaluation
- Results appear when ready

### Sidebar
- Refresh button to check evaluation status
- Pending evaluations counter
- Expandable evaluation results

## API Endpoints

**POST /evaluate**
```json
{
  "conversation_id": "uuid",
  "query": "user message",
  "response": "assistant response"
}
```

**GET /evaluation/{conversation_id}**
```json
{
  "status": "completed",
  "results": {
    "coherence": 4.5,
    "fluency": 4.8,
    "response_quality": 4.2
  }
}
```

## Usage

1. Start services with `./start.sh`
2. Open Streamlit (usually http://localhost:8501)
3. Chat with ChatGPT
4. Click "🔄 Refresh Status" in sidebar to see evaluations
5. Expand "📊 Evaluation" under messages to see scores

## Notes

- Evaluations run async (don't block chat)
- Results stored in memory (restart clears)
- Each message gets unique evaluation
- Refresh sidebar to update status
