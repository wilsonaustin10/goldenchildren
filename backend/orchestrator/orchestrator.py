"""
Orchestrator module for handling user queries, detecting intent, and executing actions.
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from pydantic import BaseModel

class UserQuery(BaseModel):
    """Model for user query input."""
    query: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class IntentResponse(BaseModel):
    """Model for intent detection response."""
    intent: str
    confidence: float
    entities: Dict[str, Any] = {}
    action_params: Dict[str, Any] = {}

class ActionResult(BaseModel):
    """Model for action execution result."""
    success: bool
    data: Any = None
    error: Optional[str] = None

class Orchestrator:
    """
    Main orchestrator class that coordinates intent detection and action execution.
    """
    
    def __init__(self):
        """Initialize the orchestrator with required components."""
        from .intent_detection import IntentDetector, EXAMPLE_INTENTS
        from .actions import default_registry
        
        # Initialize intent detector with example intents
        self.intent_detector = IntentDetector(EXAMPLE_INTENTS)
        
        # Use the default action registry
        self.action_registry = default_registry
        
        logger.info("Orchestrator initialized with intent detector and action registry")
    
    async def process_query(self, user_query: UserQuery) -> Dict[str, Any]:
        """
        Process a user query by detecting intent and executing corresponding actions.
        
        Args:
            user_query: The user's query and context
            
        Returns:
            Dict containing the processing results
        """
        logger.info(f"Processing query: {user_query.query}")
        
        # Step 1: Detect intent from user query
        intent_response = await self.detect_intent(user_query)
        
        # Step 2: Execute action based on intent
        action_result = await self.execute_action(intent_response)
        
        # Step 3: Prepare response
        response = {
            "query": user_query.query,
            "intent": intent_response.intent,
            "confidence": intent_response.confidence,
            "result": action_result.dict(),
        }
        
        return response
    
    async def detect_intent(self, user_query: UserQuery) -> IntentResponse:
        """
        Detect intent from user query using LLM.
        
        Args:
            user_query: The user's query and context
            
        Returns:
            IntentResponse with detected intent and parameters
        """
        return await self.intent_detector.detect_intent(user_query)
    
    async def execute_action(self, intent_response: IntentResponse) -> ActionResult:
        """
        Execute action based on detected intent.
        
        Args:
            intent_response: The detected intent and parameters
            
        Returns:
            ActionResult with execution results
        """
        # Get the action for the detected intent
        action = self.action_registry.get_action_for_intent(intent_response.intent)
        
        if not action:
            logger.warning(f"No action found for intent: {intent_response.intent}")
            return ActionResult(
                success=False,
                error=f"No action available for intent: {intent_response.intent}"
            )
        
        # Execute the action with the parameters from the intent response
        logger.info(f"Executing action '{action.name}' for intent '{intent_response.intent}'")
        return await action.execute(intent_response.action_params)
    
    def register_action(self, intent: str, action_handler):
        """
        Register an action handler for a specific intent.
        
        Args:
            intent: The intent name
            action_handler: The function or class that handles the action
        """
        self.action_registry.register(action_handler, intents=[intent])
        logger.info(f"Registered action handler for intent: {intent}")
