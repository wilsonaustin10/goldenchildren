#!/usr/bin/env python3
"""
Direct terminal test script for BrowserUse function call generation.
This script allows you to test the BrowserUse function call generation directly from the terminal.
"""
import asyncio
import json
import os
from dotenv import load_dotenv
from orchestrator.browser_use import default_generator

# Load environment variables
load_dotenv()

async def direct_test_browser_use():
    """
    Directly test the BrowserUse function call generation.
    """
    print("\n===== Direct BrowserUse Function Call Generator Test =====\n")
    print("This test directly generates BrowserUse function calls from your input.")
    print("Type 'exit' or 'quit' to end the test.\n")
    
    while True:
        # Get user input
        action_description = input("\nDescribe the browser actions to perform: > ")
        
        # Check if user wants to exit
        if action_description.lower() in ["exit", "quit"]:
            print("\nExiting test. Goodbye!")
            break
        
        print("\nGenerating BrowserUse function calls...")
        
        try:
            # Generate BrowserUse function calls
            plan = await default_generator.generate_function_calls(action_description)
            
            # Print the plan
            print("\nBrowserUse Function Calls:")
            plan_json = json.dumps(plan.model_dump(), indent=2)
            print(plan_json)
            
            # Save the output to a file
            output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_use_output.json")
            with open(output_file, "w") as f:
                f.write(plan_json)
            print(f"\nOutput saved to {output_file}")
            
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(direct_test_browser_use()) 