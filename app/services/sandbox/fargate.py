import logging
from typing import Dict
from .base import SandboxExecutor
from app.models.code_execution import CodeBundle

logger = logging.getLogger(__name__)

class FargateSandboxExecutor(SandboxExecutor):
    """Executes code in AWS Fargate (placeholder for future implementation)."""
    
    def __init__(self):
        """Initialize the Fargate sandbox executor."""
        super().__init__()
        logger.warning("Fargate sandbox executor is not implemented yet")
    
    def execute(self, bundle: CodeBundle) -> Dict[str, str]:
        """
        Placeholder for Fargate execution.
        
        Args:
            bundle: The code bundle to execute
            
        Returns:
            Dictionary containing error message
        """
        logger.warning("Fargate execution is not implemented yet")
        return {
            'stdout': '',
            'stderr': 'Fargate execution is not implemented yet',
            'exit_code': -1,
            'error': 'not_implemented'
        } 