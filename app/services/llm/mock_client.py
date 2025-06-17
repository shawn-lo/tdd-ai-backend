from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio

class MockDelta:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, delta, index=0, finish_reason=None):
        self.delta = delta
        self.index = index
        self.finish_reason = finish_reason

class MockChunk:
    def __init__(self, content):
        self.choices = [MockChoice(MockDelta(content))]

class MockLLMClient:
    def __init__(self):
        """Initialize the mock LLM client."""
        self.mock_responses = [
            MockChunk("Here's a concise Python implementation for the `add` function:\n\n"),
            MockChunk("```python\n"),
            MockChunk("def add(num1, num2):\n"),
            MockChunk("    return num1 + num2\n"),
            MockChunk("```\n\n"),
            MockChunk("You can use this function as follows:\n\n"),
            MockChunk("```python\n"),
            MockChunk("result = add(3, 5)\n"),
            MockChunk("print(result)  # Output: 8\n"),
            MockChunk("```")
        ]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        stream: bool = True
    ) -> AsyncGenerator[Any, None]:
        """Yield mock responses asynchronously."""
        for chunk in self.mock_responses:
            await asyncio.sleep(0.1)  # simulate delay
            yield chunk
