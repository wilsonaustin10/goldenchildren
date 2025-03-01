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
from langchain_groq import ChatGroq
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
        
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        class forward_prompt(BaseModel):
            a: int = Field(..., description="Finalized prompt to be sent to LLM")
            
        tools = [forward_prompt]
        agent_executor = create_react_agent(llm, tools=tools)
        self.agent_executor = agent_executor
    
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
            response = self.agent_executor.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
                            History: {history}
                            Current query: {message}
                            
                            Analyze this query and respond with a JSON:
                            {{"needs_more_info": true, "question": "your clarifying question"}}
                            OR
                            {{"needs_more_info": false, "final_prompt": "your generated prompt"}}
                            
                            If the user asks for you to fill up the rest or to stop asking questions, just autocomplete the rest of the details because the user may just want to see an initial draft or how well you can perform
                        """
                    }
                ]
            })
            
            # Parse the response
            try:
                output = response["messages"][-1].content
                result = json.loads(output)
                print(result, result.get("needs_more_info", False))
                if result.get("needs_more_info", False):
                    return result["question"]
                else:
                    # Process with target LLM
                    final_response = target_llm.invoke(result["final_prompt"])
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