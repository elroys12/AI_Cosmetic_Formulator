from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.analyze_schema import AnalyzeRequest, AnalyzeResponse
from app.services.ml_service import MLService
from app.services.history_service import HistoryService
from app.core.dependencies import get_current_active_user
from app.utils.logger import get_logger
import httpx
import uuid
import time

# ✅ CORRECT: No /api prefix
router = APIRouter(
    prefix="/analyze",
    tags=["Chemical Analysis"]
)

logger = get_logger(__name__)


@router.post("", response_model=AnalyzeResponse)
async def analyze_chemical(
    request: AnalyzeRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Analyze chemical properties and get AI recommendations
    
    **MODES:**
    
    1. **CHATBOT MODE** (Recommended for Frontend):
       - Send `prompt` with natural language question
       - AI generates conversational response
       - Example: "Saya butuh serum anti-aging untuk kulit sensitif"
    
    2. **PROPERTIES MODE** (Legacy/Advanced):
       - Send numeric properties (titik_didih, viskositas, etc)
       - AI analyzes based on numbers
    
    3. **HYBRID MODE** (Optional):
       - Send both prompt + properties for richer context
       - Prompt takes priority for AI understanding
    
    **FEATURES:**
    - Conversational AI explanations
    - Usage guidelines & dosage info
    - Safety notes & contraindications
    - Alternative compound recommendations
    - Conversation context support
    
    **AUTHENTICATION:** Requires valid JWT token in Authorization header
    """
    start_time = time.time()
    ml_service = MLService()
    history_service = HistoryService()
    
    input_data = request.model_dump(exclude_none=True)
    
    conversation_id = input_data.get("conversation_id")
    if not conversation_id and request.prompt:
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
    
    try:
        logger.info(f"🔍 Analyzing request for user {current_user['id']}")
        logger.info(f"📝 Input data: {input_data}")
        ml_result = await ml_service.predict_chemical(input_data)
        logger.info(f"✅ ML prediction successful")
        logger.info(f"📊 Result keys: {ml_result.keys()}")
    except HTTPException as e:
        logger.error(f"❌ HTTP Exception from ML: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Unexpected error in ML call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    
    processing_time = round(time.time() - start_time, 2)
    
    try:
        history_id = await history_service.create_history(
            user_id=current_user["id"],
            input_data=input_data,
            output_data=ml_result
        )
        logger.info(f"📝 History saved: {history_id}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to save history: {e}")
        history_id = "temp_" + uuid.uuid4().hex[:8]
    
    return {
        "success": True,
        "message": "Analysis completed successfully",
        "data": ml_result,
        "history_id": history_id,
        "conversation_id": conversation_id,
        "processing_time": processing_time
    }


@router.get("/health")
async def analyze_health_check():
    """Health check for analyze endpoint"""
    from app.config.settings import get_settings
    settings = get_settings()
    
    return {
        "success": True,
        "endpoint": "/api/analyze",
        "status": "operational",
        "ml_service_url": settings.ML_MODEL_URL,
        "features": [
            "chatbot_mode",
            "properties_mode",
            "conversation_context",
            "safety_analysis",
            "alternative_recommendations"
        ]
    }


@router.get("/ml-status")
async def ml_service_status():
    """Check ML service connectivity"""
    from app.config.settings import get_settings
    
    settings = get_settings()
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{settings.ML_MODEL_URL}/health",
                headers={"X-API-Key": settings.ML_API_KEY}
            )
            
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "success": True,
                    "ml_service": "online",
                    "url": settings.ML_MODEL_URL,
                    "response": health_data,
                    "status": "connected"
                }
            else:
                return {
                    "success": False,
                    "ml_service": "error",
                    "url": settings.ML_MODEL_URL,
                    "status_code": response.status_code,
                    "detail": response.text[:200]
                }
                
    except httpx.RequestError as e:
        return {
            "success": False,
            "ml_service": "offline",
            "url": settings.ML_MODEL_URL,
            "error": str(e),
            "status": "connection_failed"
        }
    except Exception as e:
        return {
            "success": False,
            "ml_service": "unknown_error",
            "url": settings.ML_MODEL_URL,
            "error": str(e),
            "status": "error"
        }