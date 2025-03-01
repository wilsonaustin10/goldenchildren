from orchestrator.browser_use import default_generator
import asyncio

async def main():
    plan = await default_generator.generate_function_calls(
        'Find IMDB profiles for the 2021 Oscar nominated actors for best supporting actor', 
        max_steps=15
    )
    print(plan.get_step_by_step_plan())

if __name__ == "__main__":
    asyncio.run(main()) 