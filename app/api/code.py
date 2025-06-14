from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Tuple
from enum import Enum
from app.services.sandbox import get_sandbox_executor
from app.models.code_execution import CodeBundle, CodeFile

router = APIRouter()

class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python-3.12"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CSHARP = "csharp"

class CodeRequest(BaseModel):
    """Request model for code execution."""
    language: Language
    implementation_code: str
    test_code: str

class CodeResponse(BaseModel):
    """Response model for code execution."""
    stdout: str
    stderr: str
    exit_code: int
    error: Optional[str] = None

def build_code_bundle(language: Language, implementation_code: str, test_code: str) -> CodeBundle:
    """
    Build a code bundle with test and implementation files.
    
    Args:
        language: The programming language to use
        implementation_code: The implementation code
        test_code: The test code
        
    Returns:
        CodeBundle containing the implementation and test files
    """
    # Create the code bundle
    bundle = CodeBundle()
    
    # Add implementation file
    impl_file = CodeFile(
        name="implementation.py",
        content=implementation_code.strip(),
        language=language.value,
        is_entry_point=False
    )
    bundle.add_file(impl_file)
    
    # Add test file that depends on implementation
    test_file = CodeFile(
        name="test.py",
        content=test_code.strip(),
        language=language.value,
        is_entry_point=True,
        dependencies=["implementation.py"]
    )
    bundle.add_file(test_file)
    
    return bundle

@router.post("/code", response_model=CodeResponse)
async def execute_code(request: CodeRequest) -> Dict:
    """
    Execute Python code in a sandbox environment.
    
    Args:
        request: The code execution request containing implementation and test code
        
    Returns:
        Execution results including stdout, stderr, and exit code
    """
    try:
        # Build the code bundle with test and implementation files
        bundle = build_code_bundle(request.language, request.implementation_code, request.test_code)
        
        # Get the sandbox executor
        executor = get_sandbox_executor()
        
        # Execute the code
        result = executor.execute(bundle)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing code: {str(e)}"
        )

