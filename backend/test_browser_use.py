#!/usr/bin/env python3
"""
Terminal test script for BrowserUse function call generation.
This script allows you to test the flow from user prompt to BrowserUse function calls directly from the terminal.
"""
import asyncio
import json
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from orchestrator.browser_use import default_generator
from orchestrator.intent_detection import IntentDetector, EXAMPLE_INTENTS

# Load environment variables
load_dotenv()

async def test_browser_use_generation():
    """
    Test the BrowserUse function call generation flow.
    """
    print("\n===== BrowserUse Function Call Generator Test =====\n")
    print("This test simulates the flow from user prompt to BrowserUse function calls.")
    print("Type 'exit' or 'quit' to end the test.\n")
    
    # Initialize models
    intent_detector = IntentDetector(EXAMPLE_INTENTS)
    target_llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.7,
    )
    
    # Initialize conversation history
    history: List[Dict[str, str]] = []
    
    while True:
        # Get user input
        user_message = input("\nWhat would you like your agent to do? > ")
        
        # Check if user wants to exit
        if user_message.lower() in ["exit", "quit"]:
            print("\nExiting test. Goodbye!")
            break
        
        # Add user message to history
        history.append({"role": "user", "content": user_message})
        
        print("\nProcessing your request...")
        
        try:
            # Get response from intent detector
            response = intent_detector._create_intent_collection_prompt(
                message=user_message,
                history=history,
                target_llm=target_llm
            )
            
            # Check if we need more info
            needs_more_info = isinstance(response, str) and "?" in response
            
            # Print the response
            print("\nAI Response:")
            print(response)
            
            # Add AI response to history
            history.append({"role": "assistant", "content": str(response)})
            
            # If we don't need more info, generate BrowserUse function calls
            if not needs_more_info:
                print("\nGenerating BrowserUse function calls...")
                
                # Generate BrowserUse function calls from the response
                plan = await default_generator.generate_function_calls(str(response))
                
                # Print the plan
                print("\nBrowserUse Function Calls:")
                print(json.dumps(plan.model_dump(), indent=2))
            else:
                print("\nNeed more information. Please respond to the question.")
            
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_browser_use_generation()) 