import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load env variables for API keys
load_dotenv()

from analyzer import analyze_code
from executor import extract_code_block, execute_code

app = FastAPI(title="AI Code Assistant API")

# Define request model
class AnalyzeRequest(BaseModel):
    code: str
    analysis_type: str
    language: str

# API Endpoint for analysis
@app.post("/api/analyze")
async def perform_analysis(req: AnalyzeRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set on the server.")

    try:
        # Call the existing analyzer logic
        result = analyze_code(req.code, req.analysis_type, req.language)
        
        execution_output = None
        # Always attempt to extract and execute a code block if present
        extracted_code = extract_code_block(result, req.language)
        if extracted_code:
            execution_output = execute_code(extracted_code, req.language)
        
        return {
            "result": result,
            "execution_output": execution_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files directly. We mount the static directory to /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve front page
@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
