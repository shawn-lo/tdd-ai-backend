import os
from typing import Optional
from .client import LLMClient
from .mock_client import MockLLMClient

def get_llm_client(use_mock: Optional[bool] = None) -> LLMClient | MockLLMClient:
    """Get the appropriate LLM client based on configuration."""
    if use_mock is None:
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    
    if use_mock:
        return MockLLMClient()
    return LLMClient() 