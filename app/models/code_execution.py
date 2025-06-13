from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class CodeFile:
    """Represents a single code file with its content and metadata."""
    name: str
    content: str
    language: str
    dependencies: List[str] = field(default_factory=list)  # File dependencies
    is_entry_point: bool = False

@dataclass
class CodeBundle:
    """Represents a collection of code files that form a complete program."""
    files: Dict[str, CodeFile] = field(default_factory=dict)
    entry_point: Optional[str] = None
    
    def add_file(self, file: CodeFile) -> None:
        """Add a file to the bundle."""
        self.files[file.name] = file
        if file.is_entry_point:
            self.entry_point = file.name
    
    def get_entry_point(self) -> Optional[CodeFile]:
        """Get the entry point file."""
        if self.entry_point:
            return self.files.get(self.entry_point)
        return None
    
    def get_dependencies(self, file_name: str) -> List[CodeFile]:
        """Get all dependencies for a given file."""
        file = self.files.get(file_name)
        if not file:
            return []
        
        dependencies = []
        for dep_name in file.dependencies:
            if dep := self.files.get(dep_name):
                dependencies.append(dep)
        return dependencies
    
    def validate(self) -> bool:
        """Validate the bundle structure."""
        if not self.files:
            return False
        
        if not self.entry_point:
            return False
        
        # Check that all dependencies exist
        for file in self.files.values():
            for dep in file.dependencies:
                if dep not in self.files:
                    return False
        
        return True 