#!/usr/bin/env python3
"""
API test script for BrowserUse function call generation.
This script allows you to test the BrowserUse API endpoints from the terminal.
"""
import asyncio
import json
import aiohttp
from typing import List, Dict, Any

# API base URL
API_BASE_URL = "http://localhost:8000"

async def api_test_browser_use():
    """
    Test the BrowserUse API endpoints.
    """
    print("\n===== BrowserUse API Test =====\n")
    print("This test uses the API endpoints to generate BrowserUse function calls.")
    print("Type 'exit' or 'quit' to end the test.")
    print("Type 'direct' to use the direct API endpoint.")
    print("Type 'chat' to use the chat API endpoint.\n")
    
    # Initialize conversation history
    history: List[Dict[str, str]] = []
    
    # Create HTTP session
    async with aiohttp.ClientSession() as session:
        while True:
            # Get test mode
            mode = input("\nSelect test mode (direct/chat) or exit: > ")
            
            # Check if user wants to exit
            if mode.lower() in ["exit", "quit"]:
                print("\nExiting test. Goodbye!")
                break
            
            # Check test mode
            if mode.lower() == "direct":
                # Get user input
                action_description = input("\nDescribe the browser actions to perform: > ")
                
                print("\nSending request to /api/browser-use endpoint...")
                
                try:
                    # Send request to direct API endpoint
                    async with session.post(
                        f"{API_BASE_URL}/api/browser-use",
                        json={"action_description": action_description}
                    ) as response:
                        # Check response status
                        if response.status == 200:
                            # Parse response
                            result = await response.json()
                            
                            # Print the result
                            print("\nAPI Response:")
                            print(json.dumps(result, indent=2))
                        else:
                            print(f"\nError: {response.status} - {await response.text()}")
                
                except Exception as e:
                    print(f"\nError: {str(e)}")
            
            elif mode.lower() == "chat":
                # Get user input
                message = input("\nWhat would you like your agent to do? > ")
                
                print("\nSending request to /chat/browser-use endpoint...")
                
                try:
                    # Send request to chat API endpoint
                    async with session.post(
                        f"{API_BASE_URL}/chat/browser-use",
                        json={"message": message, "history": history}
                    ) as response:
                        # Check response status
                        if response.status == 200:
                            # Parse response
                            result = await response.json()
                            
                            # Print the result
                            print("\nAPI Response:")
                            print(f"Content: {result.get('content')}")
                            print(f"Needs more info: {result.get('needs_more_info')}")
                            
                            # Add to history
                            history.append({"role": "user", "content": message})
                            history.append({"role": "assistant", "content": result.get('content', '')})
                            
                            # Print BrowserUse plan if available
                            if result.get('browser_use_plan'):
                                print("\nBrowserUse Function Calls:")
                                print(json.dumps(result.get('browser_use_plan'), indent=2))
                            elif result.get('needs_more_info'):
                                print("\nNeed more information. Please respond to the question.")
                        else:
                            print(f"\nError: {response.status} - {await response.text()}")
                
                except Exception as e:
                    print(f"\nError: {str(e)}")
            
            else:
                print("\nInvalid mode. Please select 'direct', 'chat', or 'exit'.")

if __name__ == "__main__":
    asyncio.run(api_test_browser_use()) 