from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal
import asyncio
import json

router = APIRouter()

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    language: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    code: Optional[str] = None
    tests: Optional[str] = None

async def generate_stream_response():
    # Dummy implementation - simulate streaming response
    response_parts = [
        "This is a dummy response",
        " from the AI assistant.",
        " Here's some example code:",
        "\ndef example():\n    return 'Hello, World!'",
        "\n\nAnd here are the tests:",
        "\ndef test_example():\n    assert example() == 'Hello, World!'"
    ]
    
    for part in response_parts:
        yield f"data: {json.dumps({'content': part})}\n\n"
        await asyncio.sleep(0.1)  # Simulate processing time

@router.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        generate_stream_response(),
        media_type="text/event-stream"
    ) 