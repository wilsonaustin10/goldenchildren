"""
BrowserUse function call generation module.
This module provides functionality to transform plain English actions into BrowserUse function calls.
"""
from typing import Dict, Any, List, Optional, Union
import json
from loguru import logger
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
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

class BrowserUseGenerator:
    """
    Generator for BrowserUse function calls from plain English actions.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
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
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """
        Create the prompt template for BrowserUse function call generation.
        
        Returns:
            ChatPromptTemplate for BrowserUse function call generation
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are a specialized AI that converts plain English action descriptions into BrowserUse function calls.
            
BrowserUse is a framework for browser automation that provides the following functions:

1. navigate(url: string) - Navigate to a specific URL
   Example: navigate("https://www.google.com")

2. click(selector: string) - Click on an element matching the selector
   Example: click("#search-button")

3. type(selector: string, text: string) - Type text into an element matching the selector
   Example: type("#search-input", "AI news")

4. extract(selector: string) - Extract text content from elements matching the selector
   Example: extract(".headline")

5. wait(milliseconds: number) - Wait for a specified number of milliseconds
   Example: wait(2000)

6. waitForSelector(selector: string, timeout: number) - Wait for an element matching the selector to appear
   Example: waitForSelector(".results", 5000)

7. scrollTo(x: number, y: number) - Scroll to specific coordinates
   Example: scrollTo(0, 500)

8. scrollIntoView(selector: string) - Scroll until the element matching the selector is in view
   Example: scrollIntoView("#comments-section")

9. evaluate(functionString: string) - Evaluate a JavaScript function in the browser context
   Example: evaluate("() => { return document.title; }")
   IMPORTANT: When using evaluate, NEVER use "return document" directly. Instead, extract specific properties or use DOM methods.
   CORRECT: evaluate("() => { return window.location.href; }")
   INCORRECT: evaluate("() => { return document; }")

Your task is to convert the user's plain English action descriptions into a sequence of BrowserUse function calls.
Respond with a JSON object containing an array of function calls, where each function call has a 'name' and 'args' property.

IMPORTANT RULES:
1. You MUST return a valid JSON object with at least one function in the "functions" array.
2. Each function MUST have a "name" and "args" property.
3. The "args" property MUST be a valid JSON object.
4. DO NOT include any JavaScript code outside of the JSON structure.
5. When using the 'evaluate' function, make sure the JavaScript code is properly escaped as a string.
6. NEVER use 'return document' in evaluate functions. Always extract specific properties or use DOM methods.
7. If you're unsure about the exact selectors, make reasonable guesses based on common web patterns.
8. For downloading or saving files, use click operations on appropriate buttons rather than evaluate.
9. YOUR ENTIRE RESPONSE MUST BE A VALID JSON OBJECT. DO NOT INCLUDE ANY TEXT BEFORE OR AFTER THE JSON.
10. For IMDB profiles, use navigate to go directly to the actor's page when possible (e.g., navigate("https://www.imdb.com/name/nm0000123/")).

Example:
User: "Go to Google, search for 'latest AI news', and extract the headlines"
Response:
{
  "functions": [
    {
      "name": "navigate",
      "args": {
        "url": "https://www.google.com"
      }
    },
    {
      "name": "type",
      "args": {
        "selector": "input[name='q']",
        "text": "latest AI news"
      }
    },
    {
      "name": "click",
      "args": {
        "selector": "input[name='btnK'], button[type='submit']"
      }
    },
    {
      "name": "waitForSelector",
      "args": {
        "selector": ".g",
        "timeout": 5000
      }
    },
    {
      "name": "extract",
      "args": {
        "selector": ".g h3"
      }
    }
  ],
  "explanation": "This sequence navigates to Google, searches for 'latest AI news', waits for results to load, and extracts the headlines."
}

Example for saving a document:
User: "Go to an online notepad, type 'Hello World', and save it as test.txt"
Response:
{
  "functions": [
    {
      "name": "navigate",
      "args": {
        "url": "https://onlinenotepad.org/notepad"
      }
    },
    {
      "name": "waitForSelector",
      "args": {
        "selector": "textarea, [contenteditable='true']",
        "timeout": 5000
      }
    },
    {
      "name": "type",
      "args": {
        "selector": "textarea, [contenteditable='true']",
        "text": "Hello World"
      }
    },
    {
      "name": "click",
      "args": {
        "selector": "button:contains('Save'), .save-button, [aria-label='Save']"
      }
    },
    {
      "name": "waitForSelector",
      "args": {
        "selector": "input[type='text'], input[placeholder*='file'], input[name='filename']",
        "timeout": 5000
      }
    },
    {
      "name": "type",
      "args": {
        "selector": "input[type='text'], input[placeholder*='file'], input[name='filename']",
        "text": "test.txt"
      }
    },
    {
      "name": "click",
      "args": {
        "selector": "button:contains('Save'), button:contains('Download'), .download-button"
      }
    }
  ],
  "explanation": "This sequence navigates to an online notepad, types 'Hello World', saves the document, and names it test.txt."
}

Example for finding IMDB profiles:
User: "Find IMDB profiles for the 2021 Oscar nominated actors for best supporting actor"
Response:
{
  "functions": [
    {
      "name": "navigate",
      "args": {
        "url": "https://www.google.com"
      }
    },
    {
      "name": "type",
      "args": {
        "selector": "input[name='q']",
        "text": "2021 Oscar nominees best supporting actor"
      }
    },
    {
      "name": "click",
      "args": {
        "selector": "input[name='btnK'], button[type='submit']"
      }
    },
    {
      "name": "waitForSelector",
      "args": {
        "selector": ".g",
        "timeout": 5000
      }
    },
    {
      "name": "extract",
      "args": {
        "selector": ".g h3"
      }
    },
    {
      "name": "navigate",
      "args": {
        "url": "https://www.imdb.com/name/nm1363944/"
      },
      "description": "Daniel Kaluuya's IMDB profile"
    },
    {
      "name": "navigate",
      "args": {
        "url": "https://www.imdb.com/name/nm1541953/"
      },
      "description": "Leslie Odom Jr.'s IMDB profile"
    },
    {
      "name": "navigate",
      "args": {
        "url": "https://www.imdb.com/name/nm0705562/"
      },
      "description": "Paul Raci's IMDB profile"
    },
    {
      "name": "navigate",
      "args": {
        "url": "https://www.imdb.com/name/nm0056187/"
      },
      "description": "Sacha Baron Cohen's IMDB profile"
    },
    {
      "name": "navigate",
      "args": {
        "url": "https://www.imdb.com/name/nm3147751/"
      },
      "description": "Lakeith Stanfield's IMDB profile"
    }
  ],
  "explanation": "This sequence searches for the 2021 Oscar nominees for Best Supporting Actor and navigates to each actor's IMDB profile."
}

Always use appropriate selectors based on common patterns for popular websites.

Remember: Your response MUST be a valid JSON object with at least one function in the "functions" array. DO NOT include any text before or after the JSON.
"""),
            ("user", "{action_description}")
        ])
    
    async def generate_function_calls(self, action_description: str) -> BrowserUsePlan:
        """
        Generate BrowserUse function calls from a plain English action description.
        
        Args:
            action_description: Plain English description of the actions to perform
            
        Returns:
            BrowserUsePlan with the generated function calls
        """
        try:
            # Log the action description
            logger.info(f"Generating BrowserUse function calls for: {action_description}")
            
            # Generate the function calls
            response = await self.llm.ainvoke(
                self.prompt.format(action_description=action_description)
            )
            
            # Parse the response
            content = response.content
            logger.debug(f"Raw response: {content}")
            
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
                    return self._create_fallback_plan(action_description)
            
            # Parse the JSON
            try:
                result = json.loads(content)
                
                # Check if functions array is empty or not present
                if not result.get("functions", []):
                    logger.warning("Received empty functions array, using fallback")
                    return self._create_fallback_plan(action_description)
                
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
                    return self._create_fallback_plan(action_description)
                
                return BrowserUsePlan(
                    functions=functions,
                    explanation=result.get("explanation", None),
                    action_description=action_description
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                return self._create_fallback_plan(action_description)
            
        except Exception as e:
            # Improved error handling to catch and log the specific error
            error_msg = str(e)
            logger.error(f"Error generating BrowserUse function calls: {error_msg}")
            return self._create_fallback_plan(action_description)
    
    def _create_fallback_plan(self, action_description: str) -> BrowserUsePlan:
        """
        Create a fallback plan when function call generation fails.
        
        Args:
            action_description: The original action description
            
        Returns:
            A simple BrowserUsePlan with basic function calls
        """
        logger.info("Creating fallback plan")
        
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
            
            # Extract number of actors to find
            num_actors = 5  # Default
            num_match = re.search(r'first (\d+)', action_lower)
            if num_match:
                try:
                    num_actors = int(num_match.group(1))
                except ValueError:
                    pass
            
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
            
            # Add functions to search for each actor's IMDB profile
            for i in range(1, num_actors + 1):
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
                        args={"functionString": "() => { return window.location.href; }"}
                    )
                ]
                functions.extend(actor_functions)
            
            return BrowserUsePlan(
                functions=functions,
                explanation=f"Fallback plan: Search for {year} Oscar nominees for {category}, then find IMDB profiles for {num_actors} actors",
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
            
            return BrowserUsePlan(
                functions=[
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
                ],
                explanation=f"Fallback plan: Search YouTube for '{search_term}', paste results to {notepad_url}, and save as {filename}",
                action_description=action_description
            )
        
        # Case: YouTube search
        elif "youtube" in action_lower and "search" in action_lower:
            search_term = self._extract_search_term(action_description)
            return BrowserUsePlan(
                functions=[
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
                ],
                explanation=f"Fallback plan: Search YouTube for '{search_term}'",
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
            
            functions = [
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
            
            # Add save functionality if needed
            if save_document:
                functions.extend([
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
                ])
            
            explanation = f"Fallback plan: Search for '{search_term}' and paste results to {notepad_url}"
            if save_document:
                explanation += f" and save as {filename}"
            
            return BrowserUsePlan(
                functions=functions,
                explanation=explanation,
                action_description=action_description
            )
        
        # Case: General search
        elif "search" in action_lower:
            search_term = self._extract_search_term(action_description)
            return BrowserUsePlan(
                functions=[
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
                ],
                explanation=f"Fallback plan: Search Google for '{search_term}'",
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
                ],
                explanation=f"Fallback plan: Navigate to {url}",
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