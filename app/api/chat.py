from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, AsyncGenerator
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
    usage: Optional[TokenUsage] = None

class CodeStartChunk(BaseModel):
    type: Literal["code_start"]
    language: str
    usage: Optional[TokenUsage] = None

class CodeEndChunk(BaseModel):
    type: Literal["code_end"]
    usage: Optional[TokenUsage] = None

class ErrorChunk(BaseModel):
    type: Literal["error"]
    error: str
    code: str

class DoneChunk(BaseModel):
    type: Literal["done"]
    finish_reason: Literal["stop", "length", "function_call", "user_abort"]
    usage: Optional[TokenUsage] = None

async def send_chunk(chunk: BaseModel) -> str:
    """Convert a chunk to JSON and add newline."""
    return json.dumps(chunk.model_dump()) + "\n"

async def send_start() -> str:
    """Send the start chunk."""
    start_msg = StartChunk(type="start")
    return await send_chunk(start_msg)

async def send_token(token: str, index: int) -> str:
    """Send a token chunk."""
    token_msg = TokenChunk(
        type="token",
        token=token + " ",
        role="assistant",
        index=index,
    )
    return await send_chunk(token_msg)

async def send_code_start(language: str) -> str:
    """Send a code start chunk."""
    code_start = CodeStartChunk(
        type="code_start",
        language=language
    )
    return await send_chunk(code_start)

async def send_code_end() -> str:
    """Send a code end chunk."""
    code_end = CodeEndChunk(type="code_end")
    return await send_chunk(code_end)

async def send_done(finish_reason: Literal["stop", "length", "function_call", "user_abort"] = "stop") -> str:
    """Send the done chunk."""
    done_msg = DoneChunk(
        type="done",
        finish_reason=finish_reason
    )
    return await send_chunk(done_msg)

async def send_error(error: str, code: str = "internal_error") -> str:
    """Send an error chunk."""
    error_msg = ErrorChunk(
        type="error",
        error=error,
        code=code
    )
    return await send_chunk(error_msg)

async def process_token(token: str, index: int) -> AsyncGenerator[str, None]:
    """Process a single token and yield appropriate chunks."""
    # Check if this token starts a code block
    if "def" in token:
        yield await send_code_start("python")
    
    # Send the token
    yield await send_token(token, index)
    
    # Check if this token ends a code block
    if "!" in token:
        yield await send_code_end()

@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    async def generate_stream_response():
        try:
            # Simulate streaming response with properly indented code
            response_text = """Here's a simple Python function:

```python
def greet(name: str) -> str:
    return f'Hello, {name}!'
```

And here's a TypeScript interface:

```typescript
interface User {
    id: number;
    name: string;
    email: string;
}
```"""
            # Split by newlines to preserve indentation
            lines = response_text.split('\n')
            
            # Send start message
            yield await send_start()
            
            # Process each line
            for i, line in enumerate(lines):
                async for chunk in process_token(line, i):
                    yield chunk
                await asyncio.sleep(0.1)  # Simulate processing delay
            
            # Send done message
            yield await send_done()
            
        except Exception as e:
            yield await send_error(str(e))

    return StreamingResponse(
        generate_stream_response(),
        media_type="application/x-ndjson"
    ) 