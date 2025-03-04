"""
Intent detection module using LangChain and LLMs.
"""
from typing import Dict, Any, List, Optional
import os
from loguru import logger
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
from langchain.agents import create_tool_calling_agent
from langgraph.prebuilt import create_react_agent

from .orchestrator import UserQuery, IntentResponse

# Load environment variables
load_dotenv()

class Intent(BaseModel):
    """Model for an intent definition."""
    name: str
    description: str
    required_entities: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)

class IntentDetector:
    """
    Intent detector using LangChain and LLMs.
    """
    
    def __init__(self, intents: List[Intent], model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the intent detector with a list of possible intents.
        
        Args:
            intents: List of possible intents
            model_name: Name of the LLM model to use
        """
        self.intents = intents
        self.model_name = model_name
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0,  # Use deterministic outputs for intent detection
        )
        
        # Create intent detection prompt
        self.intent_prompt = self._create_intent_prompt()
        
        # Create LLMChain for intent detection
        self.intent_chain = LLMChain(
            llm=self.llm,
            prompt=self.intent_prompt,
            output_key="intent_analysis"
        )
        
        logger.info(f"Intent detector initialized with {len(intents)} intents")
        
        llm = ChatOpenAI(
            model=model_name,
        )
        class forward_prompt(BaseModel):
            prompt: str = Field(
                description="Prompt to send to LLM for intent analysis."  # Shortened description
            )
        
        tools = []
        
        class Response(BaseModel):
            """Response."""

            needs_more_info: str = Field(description="Whether the model needs more info before making an action")
            response: str = Field(description="The response to the user")

        agent_executor = llm.bind_tools(tools)
        self.prompt_refiner = agent_executor
    
    def _create_intent_collection_prompt(self, message: str, history: List[dict], target_llm) -> str:
        """
        Create a prompt based on message and history.
        
        Args:
            message: Initial user message
            history: Conversation history
            target_llm: The target LLM to send the final prompt to
        
        Returns:
            str: The generated prompt
        """
        try:
            # Run the agent executor
            messages = [
                ("system","""You are a helpful AI assistant that collects information before acting. 
                        Analyze the query and respond in JSON format with either a clarifying question or a final prompt.
                        Format: {"needs_more_info": boolean, "response": string}
                        """),
                ("human", f"""
                            History: {history}
                            Current query: {message}
                            
                            Analyze this query and respond in a strictly JSON format (i.e. **do not output markdown**):
                            {{"needs_more_info": true, "response": "your clarifying question"}}
                            OR
                            {{"needs_more_info": false, "response": "your generated prompt"}}
                        """)
            ]
            response = self.prompt_refiner.invoke(messages)
            
            # Parse the response
            try:
                output = response.content
                cleaned_response = output.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:-3]  # Remove ```json and ``` markers
                
                result = json.loads(output)
                print(result, result.get("needs_more_info", False))
                
                if result.get("needs_more_info", False):
                    return result["response"]
                else:
                    # Process with target LLM
                    final_prompt = f"""Based on the following user request, create a concise summary of the essential requirements and intended actions:

User request: {result["response"]}

Focus on extracting:
1. The main objective
2. Key requirements
3. Any specific constraints or preferences"""
            
                    messages = [
                        ("human", final_prompt)
                    ]
                    final_response = self.prompt_refiner.invoke(messages)
                    return final_response.content
                    
            except json.JSONDecodeError:
                logger.error("Failed to parse agent response as JSON")
                return "I encountered an error processing your request."
                
        except Exception as e:
            logger.error(f"Error in intent collection: {str(e)}")
            return f"Error: {str(e)}"
    
    def _create_intent_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for intent detection.
        
        Returns:
            PromptTemplate for intent detection
        """
        # Create a string with all intent definitions
        intent_definitions = ""
        for i, intent in enumerate(self.intents, 1):
            intent_definitions += f"{i}. {intent.name}: {intent.description}\n"
            if intent.examples:
                intent_definitions += "   Examples:\n"
                for example in intent.examples:
                    intent_definitions += f"   - {example}\n"
            intent_definitions += "\n"
        
        template = """
        You are an intent detection system. Your task is to analyze the user's query and determine the most likely intent.
        
        Available intents:
        {intent_definitions}
        
        User query: {query}
        
        Analyze the query and respond with a JSON object containing:
        1. "intent": The name of the most likely intent
        2. "confidence": A number between 0 and 1 indicating your confidence
        3. "entities": A dictionary of entities extracted from the query
        4. "action_params": A dictionary of parameters needed for the action
        
        If none of the intents match, use "unknown" as the intent name.
        
        JSON response:
        """
        
        return PromptTemplate(
            input_variables=["query"],
            partial_variables={"intent_definitions": intent_definitions},
            template=template
        )
    
    async def detect_intent(self, user_query: UserQuery) -> IntentResponse:
        """
        Detect intent from user query.
        
        Args:
            user_query: The user's query and context
            
        Returns:
            IntentResponse with detected intent and parameters
        """
        try:
            # Run the intent detection chain
            result = await self.intent_chain.arun(query=user_query.query)
            
            # Parse the result (in a real implementation, you'd parse the JSON response)
            # This is a placeholder for demonstration
            logger.info(f"Raw LLM response: {result}")
            
            # In a real implementation, you would parse the JSON from the LLM response
            # For now, we'll return a placeholder
            return IntentResponse(
                intent="search_web",  # Placeholder
                confidence=0.9,  # Placeholder
                entities={"query": user_query.query},  # Placeholder
                action_params={"search_term": user_query.query}  # Placeholder
            )
            
        except Exception as e:
            logger.error(f"Error in intent detection: {str(e)}")
            return IntentResponse(
                intent="unknown",
                confidence=0.0,
                entities={},
                action_params={}
            )

# Example intents for demonstration
EXAMPLE_INTENTS = [
    Intent(
        name="search_web",
        description="Search the web for information",
        required_entities=["query"],
        examples=[
            "Search for the latest news about AI",
            "Find information about Python programming",
            "Look up the weather in New York"
        ]
    ),
    Intent(
        name="navigate_to",
        description="Navigate to a specific website",
        required_entities=["url"],
        examples=[
            "Go to google.com",
            "Navigate to github.com",
            "Open twitter.com"
        ]
    ),
    Intent(
        name="extract_data",
        description="Extract data from a webpage",
        required_entities=["url", "data_type"],
        examples=[
            "Extract the headlines from cnn.com",
            "Get the prices from amazon.com/products",
            "Scrape the comments from youtube.com/video"
        ]
    )
] 