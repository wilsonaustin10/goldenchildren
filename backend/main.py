"""
FastAPI application for the orchestrator.
"""
import os
from typing import Dict, Any, List, Optional
from browser.invoke_browser import BrowserUse
from orchestrator.intent_detection import EXAMPLE_INTENTS, IntentDetector
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse
import json
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from orchestrator.orchestrator import Orchestrator, UserQuery
from orchestrator.browser_use import default_generator, BrowserUsePlan

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

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

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


class ChatMessage(BaseModel):
    message: str
    history: List[Dict[str, Any]]
    

class ChatResponse(BaseModel):
    response: str
    needs_more_info: bool
    browser_use_plan: Dict[str, Any] = None

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time communication with the frontend.
    """
    await websocket.accept()
    active_connections[client_id] = websocket
    logger.info(f"WebSocket connection established for client: {client_id}")
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            # Parse the message
            message_data = json.loads(data)
            action_type = message_data.get("type", "")
            
            if action_type == "browser_use":
                # Extract the action description
                action_description = message_data.get("action_description", "")
                
                if not action_description:
                    await websocket.send_json({"error": "Action description is required"})
                    continue
                
                # Extract max_steps if provided, default to 10
                max_steps = message_data.get("max_steps", 10)
                
                # Ensure max_steps is an integer and within reasonable bounds
                try:
                    max_steps = int(max_steps)
                    if max_steps < 1:
                        max_steps = 1
                    elif max_steps > 50:  # Set an upper limit for safety
                        max_steps = 50
                except (ValueError, TypeError):
                    max_steps = 10  # Default if invalid
                
                # Generate BrowserUse function calls
                try:
                    plan = await default_generator.generate_function_calls(action_description, max_steps=max_steps)
                    
                    # Generate step-by-step plan
                    step_by_step_plan = plan.get_step_by_step_plan()
                    
                    # Generate action response
                    action_response = plan.get_action_response()
                    
                    # Send the plan back to the client - only include the step-by-step plan, not the raw functions
                    await websocket.send_json({
                        "type": "browser_use_plan",
                        "step_by_step_plan": step_by_step_plan,
                        "action_response": action_response,
                        "max_steps_used": max_steps
                    })
                    
                except Exception as e:
                    logger.error(f"Error generating BrowserUse function calls: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error generating BrowserUse function calls: {str(e)}"
                    })
            
            elif action_type == "chat":
                # Extract the message and history
                message = message_data.get("message", "")
                history = message_data.get("history", [])
                
                if not message:
                    await websocket.send_json({"error": "Message is required"})
                    continue
                
                # Initialize your models
                intent_detector = IntentDetector(EXAMPLE_INTENTS)
                target_llm = ChatOpenAI(
                    model_name="gpt-4o",
                    temperature=0.7,
                )

                try:
                    # Get response from intent detector
                    response = intent_detector._create_intent_collection_prompt(
                        message=message,
                        history=history,
                        target_llm=target_llm
                    )
                    
                    # Check if we need more info
                    needs_more_info = isinstance(response, str) and "?" in response
                    
                    # If we don't need more info, generate BrowserUse function calls
                    browser_use_plan = None
                    if not needs_more_info:
                        # Generate BrowserUse function calls from the response
                        plan = await default_generator.generate_function_calls(str(response))
                        browser_use_plan = plan.model_dump()
                    
                    # Send the response back to the client
                    await websocket.send_json({
                        "type": "chat_response",
                        "content": str(response),
                        "needs_more_info": needs_more_info,
                        "browser_use_plan": browser_use_plan
                    })
                    
                except Exception as e:
                    logger.error(f"Error in chat processing: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error in chat processing: {str(e)}"
                    })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action type: {action_type}"
                })
                
    except WebSocketDisconnect:
        # Remove the connection when the client disconnects
        if client_id in active_connections:
            del active_connections[client_id]
        logger.info(f"WebSocket connection closed for client: {client_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if client_id in active_connections:
            del active_connections[client_id]


@app.post("/start-browser")
async def start_browser(request: Request):
    """
    Starts browser use
    """
    prompt = await request.json()
    browser_use = BrowserUse()
    logger.info("Starting browser use")
    browser_use.InvokeBrowserAgent(prompt)

@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Chat endpoint that processes a single message and returns a response.
    """
    try:
        # Parse the request body
        data = await request.json()
        chat_input = ChatMessage(**data)
        
        # Initialize your models
        intent_detector = IntentDetector(EXAMPLE_INTENTS, model_name="gpt-4o-mini")
        target_llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.7,
        )

        # Get response from intent detector
        response = intent_detector._create_intent_collection_prompt(
            message=chat_input.message,
            history=chat_input.history,
            target_llm=target_llm,
        )
        
        # Return the response
        return {
            "content": str(response),
            "needs_more_info": isinstance(response, str) and "?" in response
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/browser-use")
async def chat_browser_use_endpoint(request: Request):
    """
    Chat endpoint that processes a message and returns a response with BrowserUse function calls.
    """
    try:
        # Parse the request body
        data = await request.json()
        chat_input = ChatMessage(**data)
        
        # Initialize your models
        intent_detector = IntentDetector(EXAMPLE_INTENTS)
        target_llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.7,
        )

        # Get response from intent detector
        response = intent_detector._create_intent_collection_prompt(
            message=chat_input.message,
            history=chat_input.history,
            target_llm=target_llm
        )
        
        # Check if we need more info
        needs_more_info = isinstance(response, str) and "?" in response
        
        # If we don't need more info, generate BrowserUse function calls
        browser_use_plan = None
        if not needs_more_info:
            # Generate BrowserUse function calls from the response
            print("RESPINSE", response)
            plan = await default_generator.generate_function_calls(str(response))
            browser_use_plan = plan.model_dump()
        
        # Return the response
        return {
            "content": str(response),
            "needs_more_info": needs_more_info,
            "browser_use_plan": browser_use_plan
        }
        
    except Exception as e:
        logger.error(f"Error in chat browser use endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/browser-use")
async def generate_browser_use(request: Request):
    """
    Generate BrowserUse function calls from a plain English action description.
    """
    try:
        # Parse the request body
        data = await request.json()
        action_description = data.get("action_description", "")
        
        if not action_description:
            raise HTTPException(status_code=400, detail="Action description is required")
        
        # Generate BrowserUse function calls
        plan = await default_generator.generate_function_calls(action_description)
        
        # Return the plan
        return plan.model_dump()
        
    except Exception as e:
        logger.error(f"Error generating BrowserUse function calls: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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