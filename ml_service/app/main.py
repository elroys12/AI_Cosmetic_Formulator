from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import re

# Import ai_pipeline dari tim ML
try:
    from app.ai_pipeline import safe_kickoff
    from app.config import get_ml_settings
except ImportError:
    from ai_pipeline import safe_kickoff
    from config import get_ml_settings

settings = get_ml_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ML Service with CrewAI Multi-Agent System",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# SCHEMAS
# =========================================================
class QueryIn(BaseModel):
    """Input schema dari tim ML"""
    topic: str

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Buatkan serum anti-aging untuk kulit sensitif"
            }
        }


class AnalyzeResponse(BaseModel):
    """Response untuk backend"""
    success: bool
    result: str
    processing_time: float = 0.0


# =========================================================
# RESPONSE PARSER (untuk backend)
# =========================================================
def parse_crew_output_to_structured(crew_text: str) -> dict:
    """
    Parse CrewAI text output menjadi structured JSON
    untuk kompatibilitas dengan backend
    """
    try:
        # Try to extract JSON if embedded
        json_match = re.search(r'\{.*\}', crew_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    # Fallback: create structured response from text
    return {
        "formula": "N/A",
        "smiles": "N/A",
        "nama_senyawa": "CrewAI Recommendation",
        "sifat_kimia": {},
        "justifikasi": crew_text[:500],
        "description": crew_text,
        "recommendations": [],
        "confidence_score": 0.85,
        "sources": ["CrewAI Multi-Agent"],
        "_metadata": {
            "source": "crewai",
            "mode": "multi_agent",
            "agents": ["data_agent", "chemical_agent", "formulation_agent"]
        }
    }


# =========================================================
# ENDPOINTS
# =========================================================
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: QueryIn):
    """
    Main endpoint - Compatible dengan tim ML
    """
    import time
    start_time = time.time()
    
    try:
        print(f"🔍 Analyzing: {req.topic}")
        
        # Call CrewAI
        result = safe_kickoff({"topic": req.topic})
        
        processing_time = time.time() - start_time
        
        print(f"✅ CrewAI completed in {processing_time:.2f}s")
        
        return {
            "success": True,
            "result": str(result),
            "processing_time": round(processing_time, 2)
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/predict")
async def predict_structured(req: QueryIn):
    """
    Structured endpoint - untuk backend yang expect JSON
    """
    import time
    start_time = time.time()
    
    try:
        print(f"🔍 Predict (structured): {req.topic}")
        
        # Call CrewAI
        crew_result = safe_kickoff({"topic": req.topic})
        
        # Parse to structured
        structured = parse_crew_output_to_structured(str(crew_result))
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "data": structured,
            "processing_time": round(processing_time, 2),
            "model_version": "1.0.0-crewai",
            "ai_model": "gemini-2.0-flash-exp-multi-agent"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check"""
    import os
    
    # Check data files
    data_dir = os.environ.get("DATA_DIR", "data")
    data_files = {}
    
    try:
        data_files = {
            "chemicals": os.path.exists(f"{data_dir}/chemicals_with_embeddings.csv"),
            "products": os.path.exists(f"{data_dir}/products_with_embeddings.csv"),
            "relations": os.path.exists(f"{data_dir}/relations_with_embeddings.csv")
        }
    except:
        data_files = {"error": "Could not check data files"}
    
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "data_dir": data_dir,
        "data_files": data_files,
        "crewai_enabled": True,
        "agents": ["data_agent", "chemical_agent", "formulation_agent"]
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "analyze": "POST /analyze (CrewAI raw output)",
            "predict": "POST /predict (Structured JSON)",
            "health": "GET /health"
        },
        "powered_by": "CrewAI Multi-Agent System"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)