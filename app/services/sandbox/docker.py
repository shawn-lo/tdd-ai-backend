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
    """Executes code in a Docker container or Finch container."""
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the Docker/Finch sandbox executor.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        super().__init__()
        self.timeout = timeout
        self.use_finch = os.getenv('USE_FINCH', 'false').lower() == 'true'
        self.container_command = self._get_container_command()
        self._check_container_availability()
    
    def _get_container_command(self) -> str:
        """Get the full path to the container command."""
        if self.use_finch:
            # Try to find finch in common locations
            finch_paths = [
                '/usr/local/bin/finch',
                '/opt/homebrew/bin/finch',
                '/Users/tianyulu/.toolbox/bin/finch',
                'finch'  # fallback to PATH
            ]
            
            for path in finch_paths:
                if os.path.exists(path):
                    return path
            
            # If not found in common paths, try which
            try:
                result = subprocess.run(['which', 'finch'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
                
            return 'finch'  # fallback
        else:
            return '/usr/local/bin/docker'
    
    def _check_container_availability(self) -> None:
        """Check if Docker or Finch is available and running."""
        try:
            # Check if container command exists
            result = subprocess.run(
                ['which', self.container_command],
                capture_output=True,
                text=True,
                env=os.environ
            )
            if result.returncode != 0:
                raise RuntimeError(f"{self.container_command.capitalize()} is not installed. Please install {self.container_command.capitalize()} first.")
            
            # Check if container daemon is running
            if self.use_finch:
                result = subprocess.run(
                    [self.container_command, 'system', 'info'],
                    capture_output=True,
                    text=True,
                    env=os.environ
                )
            else:
                result = subprocess.run(
                    [self.container_command, 'info'],
                    capture_output=True,
                    text=True,
                    env=os.environ
                )
            
            if result.returncode != 0:
                raise RuntimeError(f"{self.container_command.capitalize()} daemon is not running. Please start {self.container_command.capitalize()}.")
            
        except FileNotFoundError:
            raise RuntimeError(f"{self.container_command.capitalize()} is not installed. Please install {self.container_command.capitalize()} first.")
        except Exception as e:
            raise RuntimeError(f"Error checking {self.container_command.capitalize()} availability: {str(e)}")
    
    def _ensure_test_imports_implementation(self, bundle: CodeBundle) -> None:
        """
        Ensure the test file imports from the implementation file.
        
        Args:
            bundle: The code bundle containing test and implementation files
        """
        test_file = bundle.get_entry_point()
        if not test_file or not test_file.name.endswith('.py'):
            return
            
        # Check if the import statement is already present
        import_statement = "from implementation import *"
        if import_statement not in test_file.content:
            # Add the import statement at the beginning of the file
            test_file.content = f"{import_statement}\n\n{test_file.content}"
    
    def execute(self, bundle: CodeBundle) -> Dict[str, str | int | None]:
        """
        Execute code bundle in a Docker or Finch container.
        
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
            # Ensure test file imports from implementation
            self._ensure_test_imports_implementation(bundle)
            
            # Create a temporary directory for the code
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Write all files to the temporary directory
                for file in bundle.files.values():
                    file_path = temp_path / file.name
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(file.content)
                    logger.info(f"Wrote file {file.name} with content:\n{file.content}")
                
                # Get entry point file
                entry_point = bundle.get_entry_point()
                if not entry_point:
                    return {
                        'stdout': '',
                        'stderr': 'No entry point specified',
                        'exit_code': -1,
                        'error': 'no_entry_point'
                    }
                
                # Build container command
                if self.use_finch:
                    container_cmd = [
                        self.container_command, 'run',
                        '--rm',  # Remove container after execution
                        '--network=none',  # No network access
                        '--memory=100m',  # Memory limit
                        '--cpus=0.5',  # CPU limit
                        '--pids-limit=50',  # Process limit
                        '-v', f'{temp_dir}:/code:ro',  # Mount code directory read-only
                        f'python-sandbox:{entry_point.language}',  # Use language-specific image
                        '--entrypoint', f'/code/{entry_point.name}'  # Pass the entry point file as argument
                    ]
                else:
                    container_cmd = [
                        '/usr/local/bin/docker', 'run',
                        '--rm',  # Remove container after execution
                        '--network=none',  # No network access
                        '--memory=100m',  # Memory limit
                        '--cpus=0.5',  # CPU limit
                        '--pids-limit=50',  # Process limit
                        '-v', f'{temp_dir}:/code:ro',  # Mount code directory read-only
                        f'python-sandbox:{entry_point.language}',  # Use language-specific image
                        '--entrypoint', f'/code/{entry_point.name}'  # Pass the entry point file as argument
                    ]
                
                logger.info(f"Executing {self.container_command.capitalize()} command: {' '.join(container_cmd)}")
                
                # Execute in container
                process = subprocess.Popen(
                    container_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=os.environ,  # pass environment variables for Finch
                )
                
                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                    logger.info(f"{self.container_command.capitalize()} execution result - stdout: {stdout}, stderr: {stderr}, exit_code: {process.returncode}")
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
            logger.error(f"Error executing code in {self.container_command.capitalize()}: {str(e)}", exc_info=True)
            return {
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1,
                'error': 'execution_error'
            } 