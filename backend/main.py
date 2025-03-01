"""
FastAPI application for the orchestrator.
"""
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv

from orchestrator.orchestrator import Orchestrator, UserQuery

# Load environment variables
load_dotenv()

# Initialize the orchestrator
orchestrator = Orchestrator()

# Create FastAPI app
app = FastAPI(
    title="Orchestrator API",
    description="API for processing user queries and executing actions",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    """Model for query request."""
    query: str
    session_id: str = None
    context: Dict[str, Any] = None

class QueryResponse(BaseModel):
    """Model for query response."""
    query: str
    intent: str
    confidence: float
    result: Dict[str, Any]

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query and execute the corresponding action.
    """
    try:
        # Convert request to UserQuery
        user_query = UserQuery(
            query=request.query,
            session_id=request.session_id,
            context=request.context
        )
        
        # Process the query
        result = await orchestrator.process_query(user_query)
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

@app.get("/api/actions")
async def list_actions():
    """
    List all available actions.
    """
    return {"actions": orchestrator.action_registry.list_actions()}

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 