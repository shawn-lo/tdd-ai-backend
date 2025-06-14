import argparse
import subprocess
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--entrypoint", required=True, help="Main script to run")
    args = parser.parse_args()

    entry_path = Path(args.entrypoint)
    if not entry_path.exists():
        print(f"Entry point file does not exist: {entry_path}", file=sys.stderr)
        sys.exit(1)

    # Add the code directory to Python's path
    code_dir = entry_path.parent
    sys.path.insert(0, str(code_dir))
    
    # Debug information
    print(f"Python path: {sys.path}", file=sys.stderr)
    print(f"Code directory: {code_dir}", file=sys.stderr)
    print(f"Files in code directory:", file=sys.stderr)
    for file in code_dir.iterdir():
        print(f"  {file.name}", file=sys.stderr)

    try:
        result = subprocess.run(
            ["python", str(entry_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    except subprocess.TimeoutExpired:
        print("Execution timed out", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
