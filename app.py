import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.agent.graph import app as graph_app


app = FastAPI(title="PetCare AI Assistant")


app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    question: str


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        inputs = {"question": request.question}
        final_answer = ""
        
        # Run the graph (using astream allows us to get the final generation)
        # For a simple request/response, we allow the graph to execute fully.
        async for output in graph_app.astream(inputs):
            for key, value in output.items():
                if "generation" in value:
                    final_answer = value["generation"]
        
        if not final_answer:
            raise HTTPException(status_code=500, detail="No answer generated")
            
        return {"answer": final_answer}

    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))



