"""
BrowserUse function call generation module.
This module provides functionality to transform plain English actions into BrowserUse function calls.
"""
from typing import Dict, Any, List, Optional, Union
import json
from loguru import logger
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class BrowserUseFunction(BaseModel):
    """Model for a BrowserUse function call."""
    name: str
    args: Dict[str, Any]
    description: Optional[str] = None

class BrowserUsePlan(BaseModel):
    """Model for a BrowserUse execution plan."""
    functions: List[BrowserUseFunction]
    explanation: Optional[str] = None
    action_description: Optional[str] = None
    
    def get_step_by_step_plan(self) -> str:
        """
        Generate a step-by-step action plan from the BrowserUse functions.
        
        Returns:
            A formatted string with numbered steps describing each action
        """
        if not self.functions:
            return "No steps available in this plan."
        
        steps = []
        for i, func in enumerate(self.functions, 1):
            # Create a clear description based on the function type
            if func.name == "navigate" or func.name == "goto":
                url = func.args.get("url", "unknown URL")
                step = f"Navigate to {url}"
            
            elif func.name == "click":
                selector = func.args.get("selector", "unknown element")
                step = f"Click on {selector}"
            
            elif func.name == "type":
                selector = func.args.get("selector", "unknown element")
                text = func.args.get("text", "")
                step = f"Type '{text}' into {selector}"
            
            elif func.name == "waitForSelector":
                selector = func.args.get("selector", "unknown element")
                timeout = func.args.get("timeout", "default timeout")
                step = f"Wait for {selector} to appear (timeout: {timeout}ms)"
            
            elif func.name == "waitForNavigation":
                step = "Wait for page navigation to complete"
            
            elif func.name == "evaluate":
                function_string = func.args.get("functionString", "unknown function")
                # Use the description if available, otherwise create a generic one
                if func.description:
                    step = func.description
                else:
                    step = f"Execute JavaScript: {function_string}"
            
            elif func.name == "extract":
                selector = func.args.get("selector", "unknown element")
                step = f"Extract content from {selector}"
            
            elif func.name == "scrollTo":
                x = func.args.get("x", 0)
                y = func.args.get("y", 0)
                step = f"Scroll to position ({x}, {y})"
            
            elif func.name == "hover":
                selector = func.args.get("selector", "unknown element")
                step = f"Hover over {selector}"
            
            elif func.name == "focus":
                selector = func.args.get("selector", "unknown element")
                step = f"Focus on {selector}"
            
            elif func.name == "select":
                selector = func.args.get("selector", "unknown element")
                values = func.args.get("values", [])
                values_str = ", ".join(f"'{v}'" for v in values) if values else "no values"
                step = f"Select options {values_str} in dropdown {selector}"
            
            elif func.name == "waitForFunction":
                function_string = func.args.get("functionString", "unknown function")
                step = f"Wait for condition to be met: {function_string}"
            
            elif func.name == "screenshot":
                step = "Take a screenshot of the page"
            
            else:
                # For any other function type, use a generic description
                args_str = ", ".join(f"{k}='{v}'" for k, v in func.args.items())
                step = f"Execute {func.name}({args_str})"
            
            # Use the function's description if available and it's more informative
            if func.description and len(func.description) > len(step):
                steps.append(f"Step {i}: {func.description}")
            else:
                steps.append(f"Step {i}: {step}")
        
        # Add the explanation at the beginning if available
        result = ""
        if self.explanation:
            result += f"Plan: {self.explanation}\n\n"
        
        if self.action_description:
            result += f"Original request: {self.action_description}\n\n"
            
        result += "\n".join(steps)
        return result
    
    def get_limited_step_plan(self, max_steps: int = 5) -> str:
        """
        Generate a step-by-step action plan with a limited number of steps.
        
        Args:
            max_steps: Maximum number of steps to include in the plan
            
        Returns:
            A formatted string with numbered steps describing each action, limited to max_steps
        """
        if not self.functions:
            return "No steps available in this plan."
        
        steps = []
        for i, func in enumerate(self.functions[:max_steps], 1):
            # Create a clear description based on the function type
            if func.name == "navigate" or func.name == "goto":
                url = func.args.get("url", "unknown URL")
                step = f"Navigate to {url}"
            
            elif func.name == "click":
                selector = func.args.get("selector", "unknown element")
                step = f"Click on {selector}"
            
            elif func.name == "type":
                selector = func.args.get("selector", "unknown element")
                text = func.args.get("text", "")
                step = f"Type '{text}' into {selector}"
            
            elif func.name == "waitForSelector":
                selector = func.args.get("selector", "unknown element")
                timeout = func.args.get("timeout", "default timeout")
                step = f"Wait for {selector} to appear (timeout: {timeout}ms)"
            
            elif func.name == "waitForNavigation":
                step = "Wait for page navigation to complete"
            
            elif func.name == "evaluate":
                function_string = func.args.get("functionString", "unknown function")
                # Use the description if available, otherwise create a generic one
                if func.description:
                    step = func.description
                else:
                    step = f"Execute JavaScript: {function_string}"
            
            elif func.name == "extract":
                selector = func.args.get("selector", "unknown element")
                step = f"Extract content from {selector}"
            
            elif func.name == "scrollTo":
                x = func.args.get("x", 0)
                y = func.args.get("y", 0)
                step = f"Scroll to position ({x}, {y})"
            
            elif func.name == "hover":
                selector = func.args.get("selector", "unknown element")
                step = f"Hover over {selector}"
            
            elif func.name == "focus":
                selector = func.args.get("selector", "unknown element")
                step = f"Focus on {selector}"
            
            elif func.name == "select":
                selector = func.args.get("selector", "unknown element")
                values = func.args.get("values", [])
                values_str = ", ".join(f"'{v}'" for v in values) if values else "no values"
                step = f"Select options {values_str} in dropdown {selector}"
            
            elif func.name == "waitForFunction":
                function_string = func.args.get("functionString", "unknown function")
                step = f"Wait for condition to be met: {function_string}"
            
            elif func.name == "screenshot":
                step = "Take a screenshot of the page"
            
            else:
                # For any other function type, use a generic description
                args_str = ", ".join(f"{k}='{v}'" for k, v in func.args.items())
                step = f"Execute {func.name}({args_str})"
            
            # Use the function's description if available and it's more informative
            if func.description and len(func.description) > len(step):
                steps.append(f"Step {i}: {func.description}")
            else:
                steps.append(f"Step {i}: {step}")
        
        # Add the explanation at the beginning if available
        result = ""
        if self.explanation:
            result += f"Plan: {self.explanation}\n\n"
        
        if self.action_description:
            result += f"Original request: {self.action_description}\n\n"
        
        # Add note about limited steps if there are more steps available
        if len(self.functions) > max_steps:
            result += f"Showing first {max_steps} of {len(self.functions)} steps:\n\n"
        
        result += "\n".join(steps)
        return result
    
    def get_action_response(self) -> str:
        """
        Generate a human-readable response about what the plan will do.
        
        Returns:
            A formatted string describing what actions will be performed
        """
        if not self.functions:
            return "I don't have any actions to perform based on your request."
        
        # Get the main action types
        action_types = set()
        urls = set()
        search_terms = set()
        
        for func in self.functions:
            action_types.add(func.name)
            
            # Extract URLs
            if func.name in ["navigate", "goto"] and "url" in func.args:
                urls.add(func.args["url"])
                
            # Extract search terms
            if func.name == "type" and "text" in func.args:
                search_terms.add(func.args["text"])
        
        # Build the response
        response = "I'll help you with that. "
        
        if self.explanation:
            response += f"{self.explanation} "
        
        # Describe the main actions
        if "navigate" in action_types or "goto" in action_types:
            if urls:
                sites = ", ".join(f"'{url}'" for url in list(urls)[:3])
                if len(urls) > 3:
                    sites += f" and {len(urls) - 3} more sites"
                response += f"I'll navigate to {sites}. "
        
        if "type" in action_types and search_terms:
            terms = ", ".join(f"'{term}'" for term in list(search_terms)[:2])
            if len(search_terms) > 2:
                terms += f" and {len(search_terms) - 2} more terms"
            response += f"I'll search for {terms}. "
        
        if "click" in action_types:
            response += "I'll click on relevant elements. "
        
        if "extract" in action_types:
            response += "I'll extract the information you requested. "
        
        # Add summary of steps
        total_steps = len(self.functions)
        response += f"\n\nThis will be done in {total_steps} steps. "
        
        response += "Here's the complete plan."
        
        return response

class BrowserUseGenerator:
    """
    Generator for BrowserUse function calls from plain English actions.
    """
    
    def __init__(self, model_name: str = "gpt-4o"):
        """
        Initialize the BrowserUse function call generator.
        
        Args:
            model_name: Name of the LLM model to use
        """
        self.model_name = model_name
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.2,  # Low temperature for more deterministic outputs
        )
        
        # Create the prompt template
        self.prompt = self._create_prompt_template()
        
        logger.info(f"BrowserUse function call generator initialized with model {model_name}")
    
    def _create_prompt_template(self) -> PromptTemplate:
        """
        Create the prompt template for generating BrowserUse function calls.
        
        Returns:
            PromptTemplate for generating BrowserUse function calls
        """
        return PromptTemplate.from_template(
            """
            You are an expert at converting plain English action descriptions into a sequence of BrowserUse function calls. 
            
            # CRITICAL WARNING: NEVER RETURN ENTIRE BROWSER OBJECTS
            The following will cause fatal errors because these objects cannot be serialized:
            - NEVER use 'return document' in any evaluate function
            - NEVER use 'return window' in any evaluate function
            
            CORRECT: evaluate("() => { return window.location.href; }")
            CORRECT: evaluate("() => { return document.title; }")
            CORRECT: evaluate("() => { return Array.from(document.querySelectorAll('h1')).map(el => el.textContent); }")
            
            INCORRECT: evaluate("() => { return document; }") - THIS WILL CAUSE AN ERROR
            INCORRECT: evaluate("() => { return window; }") - THIS WILL CAUSE AN ERROR
            
            # Your Task
            Convert the following plain English action description into a sequence of BrowserUse function calls.
            
            # IMPORTANT: MAXIMUM STEPS LIMIT
            You MUST create a plan with AT MOST {max_steps} steps. This is a hard limit.
            If the task requires more steps, you must simplify or combine steps to stay within this limit.
            
            # Action Description
            {action_description}
            
            # Available BrowserUse Functions
            - goto(url: string): Navigate to the specified URL
            - click(selector: string): Click on the element matching the selector
            - type(selector: string, text: string): Type the text into the element matching the selector
            - evaluate(functionString: string): Evaluate the JavaScript function in the browser context
            - waitForSelector(selector: string, options?: object): Wait for the element matching the selector to appear
            - waitForNavigation(options?: object): Wait for the page to navigate
            - screenshot(options?: object): Take a screenshot of the page
            - scrollTo(x: number, y: number): Scroll to the specified coordinates
            - hover(selector: string): Hover over the element matching the selector
            - focus(selector: string): Focus on the element matching the selector
            - select(selector: string, values: string[]): Select options in a dropdown
            - waitForFunction(functionString: string, options?: object): Wait for the function to return true
            
            # Response Format
            Respond with a JSON object containing:
            1. An "explanation" field with a brief explanation of the approach
            2. A "functions" array with the sequence of BrowserUse function calls (MAXIMUM {max_steps} FUNCTIONS)
            
            Each function call in the array should be an object with:
            - "name": The name of the function
            - "args": An object with the arguments for the function
            - "description": A brief description of what this function call does
            
            # Example Response
            ```json
            {{
              "explanation": "To search for 'climate change news' on Google, we need to navigate to Google, type the search term, and press Enter.",
              "functions": [
                {{
                  "name": "goto",
                  "args": {{
                    "url": "https://www.google.com"
                  }},
                  "description": "Navigate to Google"
                }},
                {{
                  "name": "type",
                  "args": {{
                    "selector": "input[name='q']",
                    "text": "climate change news"
                  }},
                  "description": "Type search query"
                }},
                {{
                  "name": "evaluate",
                  "args": {{
                    "functionString": "() => {{ document.querySelector('input[name=\\'q\\']').form.submit(); }}"
                  }},
                  "description": "Submit the search form"
                }}
              ]
            }}
            ```
            
            # Important Rules
            1. Use the most efficient sequence of function calls to accomplish the task
            2. Use appropriate selectors (CSS selectors, XPath) for targeting elements
            3. Include proper waiting mechanisms (waitForSelector, waitForNavigation) when needed
            4. NEVER use 'return document' or 'return window' in evaluate functions - these will cause errors
            5. Always return valid JSON that can be parsed with JSON.parse()
            6. Make sure all function calls have the correct arguments according to their definitions
            7. NEVER EXCEED {max_steps} FUNCTION CALLS - this is a hard limit
            
            Now, convert the action description into BrowserUse function calls:
            """
        )
    
    async def generate_function_calls(self, action_description: str, max_steps: int = 10) -> BrowserUsePlan:
        """
        Generate BrowserUse function calls from a plain English action description.
        
        Args:
            action_description: Plain English description of the actions to perform
            max_steps: Maximum number of steps (function calls) to generate
            
        Returns:
            BrowserUsePlan with the generated function calls
        """
        try:
            # Log the action description
            logger.info(f"Generating BrowserUse function calls for: {action_description} (max steps: {max_steps})")
            
            # Generate the function calls
            response = await self.llm.ainvoke(
                self.prompt.format(action_description=action_description, max_steps=max_steps)
            )
            
            # Parse the response
            content = response.content
            logger.debug(f"Raw response: {content}")
            
            # Check for 'return document' or 'return window' which are common errors
            if "return document" in content or "return window" in content:
                error_type = "document" if "return document" in content else "window"
                logger.error(f"Found 'return {error_type}' in response, which is not allowed. Using fallback plan.")
                return self._create_fallback_plan(action_description, max_steps)
            
            # Extract JSON from the response if it's not already JSON
            if not content.startswith('{'):
                # Try to find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    content = content[start_idx:end_idx]
                    logger.debug(f"Extracted JSON: {content}")
                else:
                    logger.error(f"Failed to extract JSON from response: {content}")
                    # Fallback to a default function call
                    return self._create_fallback_plan(action_description, max_steps)
            
            # Parse the JSON
            try:
                result = json.loads(content)
                
                # Check if functions array is empty or not present
                if not result.get("functions", []):
                    logger.warning("Received empty functions array, using fallback")
                    return self._create_fallback_plan(action_description, max_steps)
                
                # Check for 'return document' or 'return window' in any evaluate functions
                for func in result.get("functions", []):
                    if func.get("name") == "evaluate" and isinstance(func.get("args"), dict):
                        function_string = func.get("args", {}).get("functionString", "")
                        if "return document" in function_string or "return window" in function_string:
                            error_type = "document" if "return document" in function_string else "window"
                            logger.error(f"Found 'return {error_type}' in evaluate function, which is not allowed. Using fallback plan.")
                            return self._create_fallback_plan(action_description, max_steps)
                
                # Convert to BrowserUsePlan
                functions = []
                for func in result.get("functions", []):
                    # Validate function structure
                    if not isinstance(func, dict) or "name" not in func:
                        logger.warning(f"Invalid function format: {func}")
                        continue
                        
                    # Ensure args is a dictionary
                    args = func.get("args", {})
                    if not isinstance(args, dict):
                        logger.warning(f"Invalid args format: {args}")
                        args = {}
                    
                    functions.append(BrowserUseFunction(
                        name=func.get("name", ""),
                        args=args,
                        description=func.get("description", None)
                    ))
                
                # If no valid functions were found, use fallback
                if not functions:
                    logger.warning("No valid functions found, using fallback")
                    return self._create_fallback_plan(action_description, max_steps)
                
                plan = BrowserUsePlan(
                    functions=functions,
                    explanation=result.get("explanation", None),
                    action_description=action_description
                )
                
                # Log the step-by-step plan
                logger.info(f"Generated step-by-step plan:\n{plan.get_step_by_step_plan()}")
                
                return plan
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                return self._create_fallback_plan(action_description, max_steps)
            
        except Exception as e:
            # Improved error handling to catch and log the specific error
            error_msg = str(e)
            logger.error(f"Error generating BrowserUse function calls: {error_msg}")
            
            # Special handling for 'return document' or 'return window' error
            if "return document" in error_msg or "return window" in error_msg:
                error_type = "document" if "return document" in error_msg else "window"
                logger.error(f"Detected 'return {error_type}' error in exception. Using fallback plan.")
                return self._create_fallback_plan(action_description, max_steps)
            
            # For any other error, also use the fallback plan
            return self._create_fallback_plan(action_description, max_steps)
    
    def _create_fallback_plan(self, action_description: str, max_steps: int) -> BrowserUsePlan:
        """
        Create a fallback plan when function call generation fails.
        
        Args:
            action_description: The original action description
            max_steps: Maximum number of steps (function calls) to generate
            
        Returns:
            A simple BrowserUsePlan with basic function calls
        """
        logger.info(f"Creating fallback plan with max {max_steps} steps")
        
        # Extract potential URLs from the action description
        url_match = re.search(r'https?://[^\s]+', action_description)
        url = url_match.group(0) if url_match else "https://www.google.com"
        
        # Check for common patterns in the action description
        action_lower = action_description.lower()
        
        # Case: Oscar-nominated actors search with IMDB profiles
        if ("oscar" in action_lower or "academy award" in action_lower) and "actor" in action_lower and "imdb" in action_lower:
            # Extract year if present
            year_match = re.search(r'(20\d\d|19\d\d)', action_description)
            year = year_match.group(1) if year_match else "2021"
            
            # Extract category if present
            category = "best supporting actor"
            if "lead" in action_lower or "leading" in action_lower or "best actor" in action_lower:
                category = "best actor"
            elif "supporting actress" in action_lower:
                category = "best supporting actress"
            elif "actress" in action_lower:
                category = "best actress"
            
            search_term = f"{year} Oscar nominees {category}"
            
            # Extract number of actors to find, but limit by max_steps
            # Each actor requires about 8 steps, so we can find at most max_steps/8 actors
            max_actors = max(1, max_steps // 8)
            num_actors = min(max_actors, 5)  # Default to 5 or less based on max_steps
            
            num_match = re.search(r'first (\d+)', action_lower)
            if num_match:
                try:
                    requested_actors = int(num_match.group(1))
                    num_actors = min(requested_actors, max_actors)
                except ValueError:
                    pass
            
            # Basic search functions (5 steps)
            functions = [
                # Search for Oscar nominees
                BrowserUseFunction(
                    name="navigate",
                    args={"url": "https://www.google.com"}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "input[name='q']", "text": search_term}
                ),
                BrowserUseFunction(
                    name="click",
                    args={"selector": "input[name='btnK'], button[type='submit']"}
                ),
                BrowserUseFunction(
                    name="waitForSelector",
                    args={"selector": ".g", "timeout": 5000}
                ),
                BrowserUseFunction(
                    name="extract",
                    args={"selector": ".g h3"}
                )
            ]
            
            # Add functions to search for each actor's IMDB profile, but respect max_steps
            remaining_steps = max_steps - len(functions)
            steps_per_actor = 8  # Approximate steps needed per actor
            actors_to_add = min(num_actors, remaining_steps // steps_per_actor)
            
            for i in range(1, actors_to_add + 1):
                actor_functions = [
                    # Navigate to IMDB
                    BrowserUseFunction(
                        name="navigate",
                        args={"url": "https://www.imdb.com"}
                    ),
                    BrowserUseFunction(
                        name="type",
                        args={"selector": "input#suggestion-search", "text": f"{year} Oscar nominee {category} actor {i}"}
                    ),
                    BrowserUseFunction(
                        name="click",
                        args={"selector": "button[type='submit'], #suggestion-search-button"}
                    ),
                    BrowserUseFunction(
                        name="waitForSelector",
                        args={"selector": ".findResult", "timeout": 5000}
                    ),
                    BrowserUseFunction(
                        name="click",
                        args={"selector": ".findResult:first-child .result_text a"}
                    ),
                    BrowserUseFunction(
                        name="waitForSelector",
                        args={"selector": "h1.header", "timeout": 5000}
                    ),
                    BrowserUseFunction(
                        name="extract",
                        args={"selector": "h1.header"}
                    ),
                    # Get the current URL (which is the IMDB profile)
                    BrowserUseFunction(
                        name="evaluate",
                        args={"functionString": "() => { const url = window.location.href; return url; }"}
                    )
                ]
                
                # Only add as many functions as we have room for
                remaining_functions = max_steps - len(functions)
                if remaining_functions <= 0:
                    break
                    
                functions.extend(actor_functions[:remaining_functions])
                
                # If we've reached the max, stop adding more
                if len(functions) >= max_steps:
                    break
            
            return BrowserUsePlan(
                functions=functions[:max_steps],  # Ensure we don't exceed max_steps
                explanation=f"Fallback plan: Search for {year} Oscar nominees for {category}, then find IMDB profiles for {actors_to_add} actors (limited to {max_steps} steps)",
                action_description=action_description
            )
        
        # Extract filename if present
        filename_match = re.search(r'save (?:as|it as|the document as|file as) ["\']?([^"\']+\.(?:txt|pdf|doc|docx|csv))["\']?', action_lower)
        filename = filename_match.group(1) if filename_match else "document.txt"
        
        # Case: YouTube search with notepad save
        if "youtube" in action_lower and ("notepad" in action_lower or "paste" in action_lower):
            search_term = self._extract_search_term(action_description)
            
            # Extract the notepad URL
            notepad_url_match = re.search(r'https?://[^\s]+(?:notepad|paste|pad)[^\s]*', action_description)
            notepad_url = notepad_url_match.group(0) if notepad_url_match else "https://onlinenotepad.org/notepad"
            
            # Create functions but limit to max_steps
            all_functions = [
                # First search YouTube
                BrowserUseFunction(
                    name="navigate",
                    args={"url": "https://www.youtube.com"}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "input#search", "text": search_term}
                ),
                BrowserUseFunction(
                    name="click",
                    args={"selector": "button#search-icon-legacy"}
                ),
                BrowserUseFunction(
                    name="waitForSelector",
                    args={"selector": "ytd-video-renderer", "timeout": 5000}
                ),
                BrowserUseFunction(
                    name="extract",
                    args={"selector": "ytd-video-renderer h3"}
                ),
                # Then navigate to the notepad
                BrowserUseFunction(
                    name="navigate",
                    args={"url": notepad_url}
                ),
                BrowserUseFunction(
                    name="waitForSelector",
                    args={"selector": "textarea, [contenteditable='true']", "timeout": 5000}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "textarea, [contenteditable='true']", "text": f"YouTube search results for: {search_term}"}
                ),
                # Save the document
                BrowserUseFunction(
                    name="click",
                    args={"selector": "button:contains('Save'), .save-button, [aria-label='Save']"}
                ),
                BrowserUseFunction(
                    name="waitForSelector",
                    args={"selector": "input[type='text'], input[placeholder*='file'], input[name='filename']", "timeout": 5000}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "input[type='text'], input[placeholder*='file'], input[name='filename']", "text": filename}
                ),
                BrowserUseFunction(
                    name="click",
                    args={"selector": "button:contains('Save'), button:contains('Download'), .download-button"}
                )
            ]
            
            # Take only up to max_steps functions
            functions = all_functions[:max_steps]
            
            return BrowserUsePlan(
                functions=functions,
                explanation=f"Fallback plan: Search YouTube for '{search_term}', paste results to {notepad_url}, and save as {filename} (limited to {max_steps} steps)",
                action_description=action_description
            )
        
        # Case: YouTube search
        elif "youtube" in action_lower and "search" in action_lower:
            search_term = self._extract_search_term(action_description)
            all_functions = [
                BrowserUseFunction(
                    name="navigate",
                    args={"url": "https://www.youtube.com"}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "input#search", "text": search_term}
                ),
                BrowserUseFunction(
                    name="click",
                    args={"selector": "button#search-icon-legacy"}
                ),
                BrowserUseFunction(
                    name="waitForSelector",
                    args={"selector": "ytd-video-renderer", "timeout": 5000}
                )
            ]
            
            # Take only up to max_steps functions
            functions = all_functions[:max_steps]
            
            return BrowserUsePlan(
                functions=functions,
                explanation=f"Fallback plan: Search YouTube for '{search_term}' (limited to {max_steps} steps)",
                action_description=action_description
            )
        
        # Case: Copy to notepad with save
        elif ("notepad" in action_lower or "paste" in action_lower) and "https://" in action_lower:
            # Extract the notepad URL
            notepad_url_match = re.search(r'https?://[^\s]+(?:notepad|paste|pad)[^\s]*', action_description)
            notepad_url = notepad_url_match.group(0) if notepad_url_match else "https://onlinenotepad.org/notepad"
            
            # Extract what to search for
            search_term = self._extract_search_term(action_description)
            
            # Check if we need to save the document
            save_document = "save" in action_lower or "download" in action_lower
            
            # Create all possible functions
            all_functions = [
                # First search for the content
                BrowserUseFunction(
                    name="navigate",
                    args={"url": "https://www.google.com"}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "input[name='q']", "text": search_term}
                ),
                BrowserUseFunction(
                    name="click",
                    args={"selector": "input[name='btnK'], button[type='submit']"}
                ),
                BrowserUseFunction(
                    name="waitForSelector",
                    args={"selector": ".g", "timeout": 5000}
                ),
                BrowserUseFunction(
                    name="extract",
                    args={"selector": ".g"}
                ),
                # Then navigate to the notepad
                BrowserUseFunction(
                    name="navigate",
                    args={"url": notepad_url}
                ),
                BrowserUseFunction(
                    name="waitForSelector",
                    args={"selector": "textarea, [contenteditable='true']", "timeout": 5000}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "textarea, [contenteditable='true']", "text": "Search results for: " + search_term}
                )
            ]
            
            # Add save functionality if needed and if we have room
            if save_document and len(all_functions) < max_steps:
                save_functions = [
                    BrowserUseFunction(
                        name="click",
                        args={"selector": "button:contains('Save'), .save-button, [aria-label='Save']"}
                    ),
                    BrowserUseFunction(
                        name="waitForSelector",
                        args={"selector": "input[type='text'], input[placeholder*='file'], input[name='filename']", "timeout": 5000}
                    ),
                    BrowserUseFunction(
                        name="type",
                        args={"selector": "input[type='text'], input[placeholder*='file'], input[name='filename']", "text": filename}
                    ),
                    BrowserUseFunction(
                        name="click",
                        args={"selector": "button:contains('Save'), button:contains('Download'), .download-button"}
                    )
                ]
                
                # Add as many save functions as we have room for
                remaining_space = max_steps - len(all_functions)
                all_functions.extend(save_functions[:remaining_space])
            
            # Take only up to max_steps functions
            functions = all_functions[:max_steps]
            
            explanation = f"Fallback plan: Search for '{search_term}' and paste results to {notepad_url}"
            if save_document and len(functions) > 8:  # If we included at least some save functionality
                explanation += f" and save as {filename}"
            explanation += f" (limited to {max_steps} steps)"
            
            return BrowserUsePlan(
                functions=functions,
                explanation=explanation,
                action_description=action_description
            )
        
        # Case: General search
        elif "search" in action_lower:
            search_term = self._extract_search_term(action_description)
            all_functions = [
                BrowserUseFunction(
                    name="navigate",
                    args={"url": "https://www.google.com"}
                ),
                BrowserUseFunction(
                    name="type",
                    args={"selector": "input[name='q']", "text": search_term}
                ),
                BrowserUseFunction(
                    name="click",
                    args={"selector": "input[name='btnK'], button[type='submit']"}
                )
            ]
            
            # Take only up to max_steps functions
            functions = all_functions[:max_steps]
            
            return BrowserUsePlan(
                functions=functions,
                explanation=f"Fallback plan: Search Google for '{search_term}' (limited to {max_steps} steps)",
                action_description=action_description
            )
        
        # Default case: Just navigate to the URL
        else:
            return BrowserUsePlan(
                functions=[
                    BrowserUseFunction(
                        name="navigate",
                        args={"url": url}
                    )
                ][:max_steps],  # This is redundant but keeps the pattern consistent
                explanation=f"Fallback plan: Navigate to {url} (limited to {max_steps} steps)",
                action_description=action_description
            )
    
    def _extract_search_term(self, action_description: str) -> str:
        """
        Extract a search term from an action description.
        
        Args:
            action_description: The action description
            
        Returns:
            The extracted search term
        """
        # Try to extract search term after "search for" or "find"
        action_lower = action_description.lower()
        
        if "search for" in action_lower:
            search_term = action_description.split("search for", 1)[1]
        elif "find" in action_lower:
            search_term = action_description.split("find", 1)[1]
        elif "search" in action_lower:
            search_term = action_description.split("search", 1)[1]
        elif "look for" in action_lower:
            search_term = action_description.split("look for", 1)[1]
        else:
            # Just use the whole description as a fallback
            return action_description
        
        # Clean up the search term
        search_term = search_term.strip().strip("'\"").strip()
        
        # If the search term is too long or empty, use a reasonable portion of the action description
        if not search_term or len(search_term) > 100:
            words = action_description.split()
            if len(words) > 5:
                search_term = " ".join(words[:5])
            else:
                search_term = action_description
        
        return search_term

# Create a default instance
default_generator = BrowserUseGenerator() 
default_generator = BrowserUseGenerator() 