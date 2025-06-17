from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Literal, Optional, AsyncGenerator
import json
import os
import asyncio
import logging
from dotenv import load_dotenv
from app.services.llm.factory import get_llm_client

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

router = APIRouter()

# ----------- Models -----------

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    language: Optional[str] = "python"

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
    role: Literal["assistant"] = "assistant"
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

# ----------- Chunk Senders -----------

async def send_chunk(chunk: BaseModel) -> str:
    return f"data: {json.dumps(chunk.model_dump())}\n\n"

async def send_start() -> str:
    return await send_chunk(StartChunk(type="start"))

async def send_token(token: str, index: int) -> str:
    await asyncio.sleep(0.01)  # Optional delay to simulate streaming
    return await send_chunk(TokenChunk(type="token", token=token, index=index))

async def send_code_start(language: str) -> str:
    return await send_chunk(CodeStartChunk(type="code_start", language=language))

async def send_code_end() -> str:
    return await send_chunk(CodeEndChunk(type="code_end"))

async def send_done(reason: Literal["stop", "length", "function_call", "user_abort"] = "stop") -> str:
    return await send_chunk(DoneChunk(type="done", finish_reason=reason))

async def send_error(error: str, code: str = "internal_error") -> str:
    return await send_chunk(ErrorChunk(type="error", error=error, code=code))

# ----------- Token Processor -----------

async def process_token(token: str, index: int) -> AsyncGenerator[str, None]:
    if not hasattr(process_token, "code_block_open"):
        process_token.code_block_open = False

    if "```" in token:
        if not process_token.code_block_open:
            if "python" in token:
                yield await send_code_start("python")
            elif "javascript" in token:
                yield await send_code_start("javascript")
            elif "typescript" in token:
                yield await send_code_start("typescript")
            else:
                yield await send_code_start("plaintext")
            process_token.code_block_open = True
        else:
            yield await send_code_end()
            process_token.code_block_open = False

    yield await send_token(token, index)

# ----------- Route -----------

@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    async def generate_stream_response():
        try:
            yield await send_start()

            client = get_llm_client()
            messages = [{"role": m.role, "content": m.content} for m in request.messages]

            index = 0
            async for chunk in client.chat_completion(messages=messages):
                try:
                    content = chunk.choices[0].delta.content
                except (AttributeError, IndexError):
                    continue

                if not content:
                    continue

                async for response_chunk in process_token(content, index):
                    yield response_chunk
                index += 1

            yield await send_done()

        except Exception as e:
            logger.error(f"Error in stream response: {e}")
            yield await send_error(str(e))

    return StreamingResponse(
        generate_stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
