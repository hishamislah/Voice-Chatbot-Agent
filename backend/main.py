"""
Combined entry point for Multi-Agent Chatbot with Voice Support

Usage with uvicorn:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Or run directly:
    python main.py

This will start the FastAPI server with all endpoints.
For voice, run in a SEPARATE terminal:
    cd backend && python -m voice.voice_agent dev
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
env_path = Path(__file__).parent / "env" / ".env"
load_dotenv(env_path)

# Import the FastAPI app from server - it has its own startup handler
from api.server import app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
