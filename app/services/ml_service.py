# app/services/ml_service.py

import httpx
import asyncio
from typing import Dict, Any
from fastapi import HTTPException, status
from app.config.settings import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class MLService:
    def __init__(self):
        self.ml_url = settings.ML_MODEL_URL.rstrip('/')
        self.timeout = httpx.Timeout(
            connect=30.0,
            read=300.0,
            write=30.0,
            pool=30.0
        )
        self.api_key = settings.ML_API_KEY
        self.limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=30.0
        )
        
    async def predict_chemical(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call ML Service with improved error handling and retry logic
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                return await self._make_prediction_request(input_data)
                
            except httpx.TimeoutException as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} timed out: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail="ML Service timeout after multiple retries"
                    )
                    
            except httpx.NetworkError as e:
                logger.error(f"Network error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"Network error connecting to ML Service: {str(e)}"
                    )
                    
            except httpx.RequestError as e:
                logger.error(f"Request error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"Cannot reach ML Service at {self.ml_url}"
                    )
                    
            except HTTPException:
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"ML Service error: {str(e)}"
                )
    
    async def _make_prediction_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to make the actual request
        
        ✅ FIXED: Convert 'prompt' to 'topic' for ML service
        """
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # ✅ FIX: Handle both 'prompt' and 'topic' fields
        # ML service expects 'topic', frontend sends 'prompt'
        topic = input_data.get("topic") or input_data.get("prompt", "")
        
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Missing 'prompt' or 'topic' field in request"
            )
        
        # Build ML request with 'topic' field
        ml_request = {"topic": topic}
        
        # Add properties if present
        if input_data.get("properties"):
            props = input_data["properties"]
            props_text = ", ".join([f"{k}: {v}" for k, v in props.items()])
            ml_request["topic"] = f"{topic}\n\nProperties: {props_text}"
        
        logger.info(f"📤 Calling ML Service: {self.ml_url}/predict")
        logger.debug(f"Request: {ml_request}")
        
        async with httpx.AsyncClient(
            timeout=self.timeout,
            limits=self.limits,
            follow_redirects=True
        ) as client:
            response = await client.post(
                f"{self.ml_url}/predict",
                json=ml_request,
                headers=headers
            )
            
            logger.info(f"📥 ML Service response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"ML Service Error {response.status_code}: {response.text[:200]}")
                self._handle_ml_error(response)
            
            result = response.json()
            
            # Validate response structure
            if not result.get("success", False):
                logger.error(f"ML Service returned unsuccessful: {result}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"ML Service error: {result.get('error', {}).get('message', 'Unknown error')}"
                )
            
            # Ensure data exists
            if "data" not in result:
                logger.error("ML Service response missing 'data' field")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Invalid ML Service response format"
                )
            
            logger.info("✅ ML prediction successful")
            
            data = result.get("data", {})
            
            # Ensure metadata exists
            if "_metadata" not in data:
                data["_metadata"] = {
                    "source": "ml_service",
                    "mode": "gemini_crewai"
                }
            
            return data
    
    def _handle_ml_error(self, response: httpx.Response):
        """Handle ML service errors"""
        try:
            error_data = response.json()
            error_detail = error_data.get("detail", error_data.get("message", str(error_data)))
        except:
            error_detail = response.text[:200]
        
        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ML Service authentication failed"
            )
        elif response.status_code == 422:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid request to ML Service: {error_detail}"
            )
        elif response.status_code == 503:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML Service temporarily unavailable"
            )
        elif response.status_code >= 500:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"ML Service internal error: {error_detail}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"ML Service error ({response.status_code}): {error_detail}"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ML service health"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.ml_url}/health",
                    headers={"X-API-Key": self.api_key}
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "ml_service": "online",
                        "data": response.json()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "ml_service": "error",
                        "status_code": response.status_code
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "ml_service": "offline",
                "error": str(e)
            }