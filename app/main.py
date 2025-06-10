from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, code

app = FastAPI(
    title="TDD AI Assistant Backend",
    description="Backend API for TDD AI Assistant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(code.router, prefix="/api/v1", tags=["code"])

@app.get("/")
async def root():
    return {"message": "Welcome to TDD AI Assistant Backend"} 