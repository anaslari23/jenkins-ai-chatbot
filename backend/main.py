"""
Jenkins AI Chatbot — Backend Entry Point

Start the FastAPI server:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from api.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
