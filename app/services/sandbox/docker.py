import os
import logging
import tempfile
import subprocess
from typing import Dict
from pathlib import Path
from .base import SandboxExecutor
from app.models.code_execution import CodeBundle, CodeFile

logger = logging.getLogger(__name__)

class DockerSandboxExecutor(SandboxExecutor):
    """Executes code in a Docker container."""
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the Docker sandbox executor.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        super().__init__()
        self.timeout = timeout
    
    def execute(self, bundle: CodeBundle) -> Dict[str, str]:
        """
        Execute code bundle in a Docker container.
        
        Args:
            bundle: The code bundle to execute
            
        Returns:
            Dictionary containing execution results
        """
        # Validate bundle first
        is_valid, error = self.validate_bundle(bundle)
        if not is_valid:
            return {
                'stdout': '',
                'stderr': error,
                'exit_code': -1,
                'error': 'validation_error'
            }
        
        try:
            # Create a temporary directory for the code
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Write all files to the temporary directory
                for file in bundle.files.values():
                    file_path = temp_path / file.name
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(file.content)
                
                # Get entry point file
                entry_point = bundle.get_entry_point()
                if not entry_point:
                    return {
                        'stdout': '',
                        'stderr': 'No entry point specified',
                        'exit_code': -1,
                        'error': 'no_entry_point'
                    }
                
                # Build Docker command
                docker_cmd = [
                    'docker', 'run',
                    '--rm',  # Remove container after execution
                    '--network=none',  # No network access
                    '--memory=100m',  # Memory limit
                    '--cpus=0.5',  # CPU limit
                    '--pids-limit=50',  # Process limit
                    '-v', f'{temp_dir}:/code:ro',  # Mount code directory read-only
                    f'python-sandbox:{entry_point.language}',  # Use language-specific image
                    '--entrypoint', f'/code/{entry_point.name}'  # Pass the entry point file as argument
                ]
                
                # Execute in Docker
                process = subprocess.Popen(
                    docker_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env={},  # pass empty env to reduce leakage
                )
                
                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                    return {
                        'stdout': stdout,
                        'stderr': stderr,
                        'exit_code': process.returncode,
                        'error': None
                    }
                except subprocess.TimeoutExpired:
                    process.kill()
                    return {
                        'stdout': '',
                        'stderr': f'Execution timed out after {self.timeout} seconds',
                        'exit_code': -1,
                        'error': 'timeout'
                    }
                
        except Exception as e:
            logger.error(f"Error executing code in Docker: {str(e)}", exc_info=True)
            return {
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1,
                'error': 'execution_error'
            } 