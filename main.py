from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
from nlp_utils import process_text_input

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="To-Do NLP Automation API",
    description="NLP-powered task automation endpoint for processing text inputs",
    version="1.0.0"
)

# Add CORS middleware for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TextInput(BaseModel):
    text: str

class TaskResponse(BaseModel):
    intent: str
    task_name: Optional[str] = None
    task_time: Optional[str] = None
    raw_text: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "To-Do NLP Automation API is running", "status": "healthy"}

@app.post("/process-text", response_model=TaskResponse)
async def process_text(input_data: TextInput):
    """
    Process text input for task-related intent recognition and entity extraction
    """
    try:
        logger.info(f"Processing text input: {input_data.text}")
        result = process_text_input(input_data.text)
        logger.info(f"Text processing result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing text input: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.get("/health")
async def health_check():
    """Extended health check with service status"""
    return {
        "status": "healthy",
        "service": "To-Do NLP Automation API",
        "endpoints": {
            "/process-text": "Process text input for task automation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)