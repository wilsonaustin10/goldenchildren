from langchain_openai import ChatOpenAI
import os
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()

class BrowserUse:
    def __init__(self, open_ai_key: str):
        self.open_ai_key = open_ai_key

    async def InvokeBrowserAgent(self, task: str):
        try:
            os.environ["OPENAI_API_KEY"] = self.open_ai_key
            agent = Agent(
                task=task,
                llm=ChatOpenAI(model="gpt-4o"),
            )
            result = await agent.run()
            return result
        except Exception as e:
            print(e)
        finally:
            os.environ.pop("OPENAI_API")
