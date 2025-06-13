from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
import logging
from app.models.code_execution import CodeBundle, CodeFile

logger = logging.getLogger(__name__)

class SandboxExecutor(ABC):
    """Abstract base class for sandbox executors."""
    
    def __init__(self):
        """Initialize the sandbox executor."""
        pass
    
    @abstractmethod
    def execute(self, bundle: CodeBundle) -> Dict[str, str]:
        """
        Execute code bundle in the sandbox environment.
        
        Args:
            bundle: The code bundle to execute
            
        Returns:
            Dictionary containing execution results
        """
        pass
    
    def validate_bundle(self, bundle: CodeBundle) -> Tuple[bool, Optional[str]]:
        """
        Validate code bundle for potential security issues.
        
        Args:
            bundle: The code bundle to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not bundle.validate():
            return False, "Invalid bundle structure"
        
        # List of potentially dangerous operations
        dangerous_patterns = {
            'python': [
                'import os',
                'import sys',
                'import subprocess',
                'import socket',
                'import requests',
                'import urllib',
                '__import__',
                'eval(',
                'exec(',
                'open(',
                'file(',
                'os.system',
                'subprocess.call',
                'subprocess.Popen',
                'socket.socket',
                'requests.get',
                'requests.post'
            ],
            'javascript': [
                'require(',
                'import ',
                'eval(',
                'Function(',
                'setTimeout(',
                'setInterval(',
                'fetch(',
                'XMLHttpRequest',
                'process.',
                'child_process',
                'fs.'
            ]
        }
        
        for file in bundle.files.values():
            patterns = dangerous_patterns.get(file.language.lower(), [])
            for pattern in patterns:
                if pattern in file.content:
                    return False, f"File {file.name} contains potentially dangerous operation: {pattern}"
        
        return True, None
    
    def _get_file_extension(self, language: str) -> str:
        """Get the file extension for a given language."""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c'
        }
        return extensions.get(language.lower(), 'txt') 