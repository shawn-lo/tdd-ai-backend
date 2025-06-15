from openai import OpenAI
import os
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel
import asyncio

class Message(BaseModel):
    role: str
    content: str

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        stream: bool = True
    ) -> AsyncGenerator[Any, None]:
        """Get a chat completion from the LLM."""
        def create_stream():
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=stream
            )

        # Run the OpenAI API call in a thread pool
        stream = await asyncio.to_thread(create_stream)
        
        # Process the stream asynchronously
        for chunk in stream:
            yield chunk 