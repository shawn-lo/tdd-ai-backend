from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import json
import asyncio
from datetime import datetime

router = APIRouter()

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class StartChunk(BaseModel):
    type: Literal["start"]
    usage: Optional[TokenUsage] = None

class TokenChunk(BaseModel):
    type: Literal["token"]
    token: str
    role: Literal["assistant"] = "assistant"  # Only assistant for responses
    index: int
    language: Optional[str] = None
    is_code: bool = False
    usage: Optional[TokenUsage] = None

class ErrorChunk(BaseModel):
    type: Literal["error"]
    error: str
    code: str

class DoneChunk(BaseModel):
    type: Literal["done"]
    finish_reason: Literal["stop", "length", "function_call", "user_abort"]
    usage: Optional[TokenUsage] = None

@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    async def generate_stream_response():
        try:
            # Simulate streaming response with comprehensive data
            response_text = "Here's a simple Python function:\n\ndef greet(name: str) -> str:\n    return f'Hello, {name}!'"
            tokens = response_text.split()
            
            # Send start message
            start_msg = StartChunk(
                type="start",
            )
            yield json.dumps(start_msg.model_dump()) + "\n"
            
            # Send token messages
            for i, token in enumerate(tokens):
                is_code = "def" in token or "return" in token or ":" in token
                language = "python" if is_code else None
                
                token_msg = TokenChunk(
                    type="token",
                    token=token + " ",
                    role="assistant",
                    index=i,
                    language=language,
                    is_code=is_code,
                )
                yield json.dumps(token_msg.model_dump()) + "\n"
                await asyncio.sleep(0.1)  # Simulate processing delay
            
            # Send done message
            done_msg = DoneChunk(
                type="done",
                finish_reason="stop",
            )
            yield json.dumps(done_msg.model_dump()) + "\n"
        except Exception as e:
            error_msg = ErrorChunk(
                type="error",
                error=str(e),
                code="internal_error"
            )
            yield json.dumps(error_msg.model_dump()) + "\n"

    return StreamingResponse(
        generate_stream_response(),
        media_type="application/x-ndjson"
    ) 