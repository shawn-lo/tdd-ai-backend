from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio

class MockLLMClient:
    def __init__(self):
        """Initialize the mock LLM client."""
        self.mock_responses = [
            "Here's a concise Python implementation for the `add` function:\n\n",
            "```python\n",
            "def add(num1, num2):\n",
            "    return num1 + num2\n",
            "```\n\n",
            "You can use this function as follows:\n\n",
            "```python\n",
            "result = add(3, 5)\n",
            "print(result)  # Output: 8\n",
            "```"
        ]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        stream: bool = True
    ) -> AsyncGenerator[Any, None]:
        """Get a mock chat completion."""
        class MockStream:
            def __init__(self, responses):
                self.responses = responses
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index >= len(self.responses):
                    raise StopIteration
                
                response = self.responses[self.index]
                self.index += 1
                
                class MockChoice:
                    class Delta:
                        content = response
                    choices = [Delta()]
                
                return MockChoice()

        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Create and yield from mock stream
        stream = MockStream(self.mock_responses)
        for chunk in stream:
            yield chunk 