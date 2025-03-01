"""
Action framework for executing operations based on detected intents.
This module provides a flexible, extensible system for defining and executing actions.
"""
from typing import Dict, Any, List, Optional, Protocol, Type, Callable, TypeVar, Union
import abc
import inspect
import asyncio
from loguru import logger
from pydantic import BaseModel

from .orchestrator import IntentResponse, ActionResult

# Type for action parameters
ActionParams = Dict[str, Any]

class Action(abc.ABC):
    """
    Abstract base class for all actions.
    
    Implement this class to create new action types.
    """
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The unique name of this action."""
        pass
    
    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Description of what this action does."""
        pass
    
    @abc.abstractmethod
    async def execute(self, params: ActionParams) -> ActionResult:
        """
        Execute the action with the given parameters.
        
        Args:
            params: Parameters for the action
            
        Returns:
            ActionResult with the result of the action
        """
        pass
    
    @property
    def required_params(self) -> List[str]:
        """List of required parameters for this action."""
        return []
    
    def validate_params(self, params: ActionParams) -> bool:
        """
        Validate that all required parameters are present.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if all required parameters are present, False otherwise
        """
        return all(param in params for param in self.required_params)


class ActionRegistry:
    """
    Registry for actions that can be executed by the orchestrator.
    """
    
    def __init__(self):
        """Initialize an empty action registry."""
        self._actions: Dict[str, Action] = {}
        self._intent_to_action: Dict[str, str] = {}
    
    def register(self, action: Action, intents: List[str] = None):
        """
        Register an action in the registry.
        
        Args:
            action: The action to register
            intents: Optional list of intents that map to this action
        """
        self._actions[action.name] = action
        logger.info(f"Registered action: {action.name}")
        
        if intents:
            for intent in intents:
                self._intent_to_action[intent] = action.name
                logger.info(f"Mapped intent '{intent}' to action '{action.name}'")
    
    def get_action_for_intent(self, intent: str) -> Optional[Action]:
        """
        Get the action for a given intent.
        
        Args:
            intent: The intent name
            
        Returns:
            The action for the intent, or None if no action is registered
        """
        action_name = self._intent_to_action.get(intent)
        if not action_name:
            logger.warning(f"No action registered for intent: {intent}")
            return None
        
        return self._actions.get(action_name)
    
    def get_action(self, action_name: str) -> Optional[Action]:
        """
        Get an action by name.
        
        Args:
            action_name: The name of the action
            
        Returns:
            The action, or None if no action with that name is registered
        """
        return self._actions.get(action_name)
    
    def list_actions(self) -> List[Dict[str, Any]]:
        """
        List all registered actions.
        
        Returns:
            List of action information dictionaries
        """
        return [
            {
                "name": action.name,
                "description": action.description,
                "required_params": action.required_params
            }
            for action in self._actions.values()
        ]


# Example actions using BrowserUse

class WebSearchAction(Action):
    """Action to search the web for information."""
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for information"
    
    @property
    def required_params(self) -> List[str]:
        return ["search_term"]
    
    async def execute(self, params: ActionParams) -> ActionResult:
        """
        Execute a web search.
        
        Args:
            params: Must contain 'search_term'
            
        Returns:
            ActionResult with search results
        """
        if not self.validate_params(params):
            return ActionResult(
                success=False,
                error=f"Missing required parameters. Required: {self.required_params}"
            )
        
        search_term = params["search_term"]
        logger.info(f"Searching web for: {search_term}")
        
        try:
            # In a real implementation, you would use BrowserUse here
            # For the hackathon demo, we'll simulate the search
            await asyncio.sleep(1)  # Simulate network delay
            
            # Simulated search results
            results = [
                {"title": f"Result 1 for {search_term}", "url": f"https://example.com/1"},
                {"title": f"Result 2 for {search_term}", "url": f"https://example.com/2"},
                {"title": f"Result 3 for {search_term}", "url": f"https://example.com/3"},
            ]
            
            return ActionResult(
                success=True,
                data={"results": results}
            )
            
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            return ActionResult(
                success=False,
                error=f"Error in web search: {str(e)}"
            )


class NavigateToAction(Action):
    """Action to navigate to a specific website."""
    
    @property
    def name(self) -> str:
        return "navigate_to"
    
    @property
    def description(self) -> str:
        return "Navigate to a specific website"
    
    @property
    def required_params(self) -> List[str]:
        return ["url"]
    
    async def execute(self, params: ActionParams) -> ActionResult:
        """
        Navigate to a website.
        
        Args:
            params: Must contain 'url'
            
        Returns:
            ActionResult with navigation result
        """
        if not self.validate_params(params):
            return ActionResult(
                success=False,
                error=f"Missing required parameters. Required: {self.required_params}"
            )
        
        url = params["url"]
        logger.info(f"Navigating to: {url}")
        
        try:
            # In a real implementation, you would use BrowserUse here
            # For the hackathon demo, we'll simulate the navigation
            await asyncio.sleep(1)  # Simulate network delay
            
            return ActionResult(
                success=True,
                data={"url": url, "title": f"Page title for {url}", "status": "loaded"}
            )
            
        except Exception as e:
            logger.error(f"Error in navigation: {str(e)}")
            return ActionResult(
                success=False,
                error=f"Error navigating to {url}: {str(e)}"
            )


class ExtractDataAction(Action):
    """Action to extract data from a webpage."""
    
    @property
    def name(self) -> str:
        return "extract_data"
    
    @property
    def description(self) -> str:
        return "Extract data from a webpage"
    
    @property
    def required_params(self) -> List[str]:
        return ["url", "data_type"]
    
    async def execute(self, params: ActionParams) -> ActionResult:
        """
        Extract data from a webpage.
        
        Args:
            params: Must contain 'url' and 'data_type'
            
        Returns:
            ActionResult with extracted data
        """
        if not self.validate_params(params):
            return ActionResult(
                success=False,
                error=f"Missing required parameters. Required: {self.required_params}"
            )
        
        url = params["url"]
        data_type = params["data_type"]
        logger.info(f"Extracting {data_type} from: {url}")
        
        try:
            # In a real implementation, you would use BrowserUse here
            # For the hackathon demo, we'll simulate the extraction
            await asyncio.sleep(1.5)  # Simulate network delay
            
            # Simulated extracted data
            if data_type == "headlines":
                data = [
                    "Headline 1: Important news",
                    "Headline 2: Breaking development",
                    "Headline 3: Latest update"
                ]
            elif data_type == "prices":
                data = [
                    {"item": "Product 1", "price": "$19.99"},
                    {"item": "Product 2", "price": "$29.99"},
                    {"item": "Product 3", "price": "$39.99"}
                ]
            else:
                data = [f"Extracted {data_type} item 1", f"Extracted {data_type} item 2"]
            
            return ActionResult(
                success=True,
                data={"url": url, "data_type": data_type, "extracted_data": data}
            )
            
        except Exception as e:
            logger.error(f"Error in data extraction: {str(e)}")
            return ActionResult(
                success=False,
                error=f"Error extracting {data_type} from {url}: {str(e)}"
            )


# Create a default action registry with example actions
default_registry = ActionRegistry()
default_registry.register(WebSearchAction(), intents=["search_web"])
default_registry.register(NavigateToAction(), intents=["navigate_to"])
default_registry.register(ExtractDataAction(), intents=["extract_data"]) 