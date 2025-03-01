# Intent-Based Orchestrator

A flexible orchestrator that performs actions based on the intent deduced from user queries.

## Project Structure

- `backend/`: Python FastAPI backend
  - `orchestrator/`: Core orchestrator components
    - `orchestrator.py`: Main orchestrator class
    - `intent_detection.py`: LLM-based intent detection
    - `actions.py`: Action framework and implementations
  - `main.py`: FastAPI application
- `frontend/`: Next.js frontend (to be implemented)

## Features

- LLM-based intent detection using LangChain and OpenAI
- Flexible action framework for executing operations
- Web automation capabilities using BrowserUse
- RESTful API for integration with frontend applications

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+ (for frontend)
- OpenAI API key

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```bash
   cp backend/.env.example backend/.env
   ```

4. Edit the `.env` file and add your OpenAI API key.

5. Run the backend:
   ```bash
   cd backend
   python main.py
   ```

6. The API will be available at `http://localhost:8000`.
   - API documentation: `http://localhost:8000/docs`

### Adding New Actions

To add a new action:

1. Create a new class that inherits from `Action` in `backend/orchestrator/actions.py`.
2. Implement the required methods: `name`, `description`, and `execute`.
3. Register the action in the action registry.

Example:

```python
class MyNewAction(Action):
    @property
    def name(self) -> str:
        return "my_new_action"
    
    @property
    def description(self) -> str:
        return "Description of my new action"
    
    @property
    def required_params(self) -> List[str]:
        return ["param1", "param2"]
    
    async def execute(self, params: ActionParams) -> ActionResult:
        # Implement action logic here
        return ActionResult(success=True, data={"result": "Action executed"})

# Register the action
default_registry.register(MyNewAction(), intents=["my_intent"])
```

### Adding New Intents

To add a new intent:

1. Add a new `Intent` object to the `EXAMPLE_INTENTS` list in `backend/orchestrator/intent_detection.py`.
2. Create a corresponding action for the intent.

Example:

```python
Intent(
    name="my_intent",
    description="Description of my intent",
    required_entities=["entity1", "entity2"],
    examples=[
        "Example query 1",
        "Example query 2"
    ]
)
```

## API Endpoints

- `POST /api/query`: Process a user query
  - Request body: `{"query": "your query here"}`
  - Response: Intent detection and action execution results

- `GET /api/health`: Health check endpoint

- `GET /api/actions`: List all available actions

## License

MIT 