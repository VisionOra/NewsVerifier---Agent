"""FastAPI wrapper for the FlipZen Negative News Agent.

This module provides a REST API interface to the FlipZen agent.
"""

import os
from typing import Dict, Optional, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import the agent components
try:
    from src.agent import graph, UserInput, invoke_negative_news_check
except ModuleNotFoundError:
    try:
        # Try alternative import path when running directly
        from flipzen.src.agent import graph, UserInput, invoke_negative_news_check
    except ModuleNotFoundError:
        # Final fallback for Docker environment
        import sys
        print(f"Python path: {sys.path}")
        print("Attempting direct import from agent package...")
        from src.agent.graph import graph, invoke_negative_news_check
        from src.agent.state import UserInput

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FlipZen Negative News API",
    description="API for screening entities against negative news",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model that matches the agent's UserInput
class ScreeningRequest(BaseModel):
    name: str = Field(..., description="Full name of the entity to screen")
    dob: Optional[str] = Field(None, description="Date of birth (optional)")
    nationality: Optional[str] = Field(None, description="Nationality (optional)")
    industry: Optional[str] = Field(None, description="Industry (optional)")
    jobTitle: Optional[str] = Field(None, description="Job title (optional)")

# Response model
class ScreeningResponse(BaseModel):
    report: Dict[str, Any] = Field(..., description="Screening report with analysis and findings")
    entity: Dict[str, Any] = Field(..., description="Entity information")
    status: str = Field("success", description="Status of the request")

# Error response model
class ErrorResponse(BaseModel):
    status: str = Field("error", description="Status of the request")
    message: str = Field(..., description="Error message")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "FlipZen Negative News API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/screen", response_model=ScreeningResponse)
async def screen_entity(request: ScreeningRequest):
    try:
        # Create a dictionary of input data
        input_data = {
            "name": request.name,
            "dob": request.dob,
            "nationality": request.nationality,
            "industry": request.industry,
            "jobTitle": request.jobTitle,
        }
        
        # Print the input data for debugging
        print(f"API REQUEST: Processing screening for {request.name}")
        print(f"INPUT DATA: {input_data}")
        
        # Use the wrapper function that ensures proper output structure
        print("Invoking negative news check")
        result = invoke_negative_news_check(input_data)
        print("Negative news check complete")

        print("RESULT KEYS:", list(result.keys()))
        
        # The result structure should now be much cleaner from our new graph implementation
        # Create the response object from the result
        response = {
            "report": result["report"],
            "entity": result["entity"],
            "status": "success"
        }
        
        print(f"API RESPONSE: Returning screening results for {request.name}")
        print(f"HAS NEGATIVE NEWS: {result.get('has_negative_news', False)}")
        print(f"RISK SCORE: {result.get('risk_score', 0)}")
        
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True) 