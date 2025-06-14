from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from app.services.sandbox import get_sandbox_executor
from app.models.code_execution import CodeBundle, CodeFile

router = APIRouter()

class CodeRequest(BaseModel):
    """Request model for code execution."""
    code: str

class CodeResponse(BaseModel):
    """Response model for code execution."""
    stdout: str
    stderr: str
    exit_code: int
    error: Optional[str] = None

# Test script that exercises basic Python functionality
TEST_SCRIPT = """
print('Hello from inside Docker!')
"""

@router.post("/code", response_model=CodeResponse)
async def execute_code(request: CodeRequest) -> Dict:
    """
    Execute Python code in a sandbox environment.
    
    Args:
        request: The code execution request containing the code to execute
        
    Returns:
        Execution results including stdout, stderr, and exit code
    """
    try:
        # Create a code bundle with a single file
        bundle = CodeBundle()
        
        # Add the main file with the code from the request
        main_file = CodeFile(
            name="main.py",
            content=request.code,
            language="python-3.12",
            is_entry_point=True
        )
        bundle.add_file(main_file)
        
        # Get the sandbox executor
        executor = get_sandbox_executor()
        
        # Execute the code
        result = executor.execute(bundle)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing code: {str(e)}"
        )

