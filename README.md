# TDD AI Assistant Backend

Backend API for the TDD AI Assistant application, built with FastAPI. This service provides endpoints for AI-powered code generation and test execution.

## Features

- FastAPI-based REST API
- OpenAI integration for AI-powered code generation
- Code execution in sandboxed environment
- Real-time streaming responses
- Support for multiple programming languages

## Tech Stack

- FastAPI
- Python 3.11+
- OpenAI API
- Docker (for code execution sandbox)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker (for code execution)
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tdd-ai-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the Server

Start the development server using either:

```bash
uvicorn app.main:app --reload
```

or

```bash
fastapi dev main.py
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

### Endpoints

#### Chat API

- `POST /api/v1/chat`
  - Streams AI responses for code generation and testing
  - Request body:
    ```json
    {
      "messages": [
        {
          "role": "user",
          "content": "Create a function to calculate factorial"
        }
      ],
      "language": "python"
    }
    ```
  - Response: Server-Sent Events (SSE) stream

#### Code Execution API

- `POST /api/v1/execute`
  - Executes code in a sandboxed environment
  - Request body:
    ```json
    {
      "code": "def example(): return 'Hello, World!'",
      "language": "python",
      "version": "3.11"
    }
    ```
  - Response:
    ```json
    {
      "output": "Test execution successful!",
      "error": null,
      "execution_time": 0.5
    }
    ```

## Development

### Project Structure

```
tdd-ai-backend/
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   └── code.py
│   ├── core/
│   │   └── config.py
│   └── main.py
├── venv/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

### Adding New Features

1. Create new endpoints in the appropriate module under `app/api/`
2. Update the main application in `app/main.py` to include new routers
3. Add any new dependencies to `requirements.txt`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 