# main.py

import asyncio
from src.agent.graph import app

async def main():
    print("================================")
    print("Pet Care RAG Bot is ready.")
    print("Type 'exit' to quit.")
    print("================================")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        
        inputs = {"question": user_input}
        final_generation = ""
        
        async for output in app.astream(inputs):
            for key, value in output.items():
                print(f"\n[Processing: {key}]")
                if "generation" in value:
                    final_generation = value["generation"]
        
        print("\n" + "="*20)
        print("Final Answer:")
        print("="*20)
        print(final_generation)
        print("\n" + "="*40)

if __name__ == "__main__":
    asyncio.run(main())
