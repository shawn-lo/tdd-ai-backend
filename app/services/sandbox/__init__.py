import os
from typing import Optional
from .base import SandboxExecutor
from .docker import DockerSandboxExecutor
from .fargate import FargateSandboxExecutor

def get_sandbox_executor() -> SandboxExecutor:
    """
    Get the appropriate sandbox executor based on the environment.
    
    Returns:
        SandboxExecutor instance
    """
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        return FargateSandboxExecutor()
    else:
        return DockerSandboxExecutor() 