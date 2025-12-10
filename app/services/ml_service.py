# app/services/ml_service.py

import httpx
from typing import Dict, Any
from fastapi import HTTPException, status
from app.config.settings import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class MLService:
    def __init__(self):
        self.ml_url = settings.ML_MODEL_URL.rstrip('/')
        self.timeout = 180  # ✅ Increase untuk CrewAI (min 120s)
        self.api_key = settings.ML_API_KEY
        
    async def predict_chemical(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call ML Service with CrewAI (tim ML implementation)
        """
        try:
            headers = {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Format untuk CrewAI /predict endpoint
            prompt = input_data.get("prompt", "")
            
            # Jika ada properties, tambahkan ke prompt
            if input_data.get("properties"):
                props = input_data["properties"]
                props_text = ", ".join([f"{k}: {v}" for k, v in props.items()])
                prompt = f"{prompt}\n\nProperties: {props_text}"
            
            ml_request = {"topic": prompt}
            
            logger.info(f"📤 Calling CrewAI ML Service: {ml_request}")
            
            # Call CrewAI /predict endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ml_url}/predict",
                    json=ml_request,
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"ML Service Error {response.status_code}: {response.text[:200]}")
                    self._handle_ml_error(response)
                
                result = response.json()
                
                if not result.get("success", False):
                    logger.error(f"ML Service returned unsuccessful: {result}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="ML Service returned unsuccessful response"
                    )
                
                logger.info("✅ CrewAI prediction successful")
                
                # Return structured data
                data = result.get("data", {})
                
                # Ensure metadata exists
                if "_metadata" not in data:
                    data["_metadata"] = {
                        "source": "crewai_ml_service",
                        "mode": "multi_agent"
                    }
                
                return data
                
        except httpx.TimeoutException:
            logger.error("ML Service timeout (CrewAI processing can take 60-180s)")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="ML Service request timeout (AI processing taking too long). CrewAI typically needs 1-3 minutes."
            )
        except httpx.RequestError as e:
            logger.error(f"ML Service connection error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to connect to ML Service at {self.ml_url}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ML Service call: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get prediction from ML service: {str(e)}"
            )
    
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
                detail=f"ML Service authentication failed: {error_detail}"
            )
        elif response.status_code == 422:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"ML Service validation error: {error_detail}"
            )
        elif response.status_code == 503:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML Service is currently unavailable"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error from ML Service ({response.status_code}): {error_detail}"
            )