#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Employee Policy RAG application..."

# 1. Activate virtual environment
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Virtual environment .venv not found. Please run 'python3 -m venv .venv && pip install -r requirements.txt' first."
    exit 1
fi

# 2. Check Ollama
echo "🤖 Checking Ollama local service..."
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "⚠️ Ollama is not running. Please start Ollama desktop app or run 'ollama serve'."
    echo "Proceeding anyway in case it starts up shortly..."
else
    echo "📥 Ensuring models are pulled..."
    ollama pull nomic-embed-text:latest >/dev/null &
    ollama pull qwen3:8b >/dev/null &
fi

# 3. Create policies if they don't exist
if [ ! -d "documents" ] || [ -z "$(ls -A documents/*.pdf 2>/dev/null)" ]; then
    echo "📄 Generating default policy PDF documents..."
    python create_policies.py
fi

# 4. Ingest documents if ChromaDB doesn't exist
if [ ! -d "chroma_db" ]; then
    echo "📂 Ingesting policy documents into ChromaDB..."
    PYTHONPATH=. python app/ingestion/ingest.py
fi

# 5. Check and clear port conflicts
echo "🔍 Checking port conflicts..."
for PORT in 8000 8501; do
    PID=$(lsof -t -i :$PORT || true)
    if [ ! -z "$PID" ]; then
        echo "⚠️ Port $PORT is already in use by process $PID. Stopping it..."
        kill -9 $PID 2>/dev/null || true
    fi
done

# 6. Spin up services
echo "⚡ Starting FastAPI Backend on port 8000..."
PYTHONPATH=. uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir app > backend.log 2>&1 &
BACKEND_PID=$!

echo "⏳ Waiting for FastAPI Backend to start up and become healthy..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/health | grep -q '"status":"healthy"'; then
        echo "🟢 FastAPI Backend is online and healthy!"
        break
    fi
    sleep 1
done

echo "🖥️ Starting Streamlit UI on port 8501..."
streamlit run ui.py --server.port 8501 > streamlit.log 2>&1 &
STREAMLIT_PID=$!

# Elegant shutdown handler
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $STREAMLIT_PID 2>/dev/null || true
    echo "👋 Done!"
}
trap cleanup EXIT

echo "🎉 All services started successfully!"
echo "--------------------------------------------------"
echo "🔗 Streamlit Web UI: http://localhost:8501"
echo "🔗 FastAPI Backend:  http://127.0.0.1:8000/docs"
echo "--------------------------------------------------"
echo "Logs are saved to backend.log and streamlit.log."
echo "Press [CTRL+C] to stop both services."

# Keep script running to monitor background processes
wait
