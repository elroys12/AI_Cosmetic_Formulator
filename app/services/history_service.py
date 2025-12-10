# app/services/history_service.py

from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from app.db.supabase_client import get_supabase_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def create_history(
        self, 
        user_id: str, 
        input_data: Dict[str, Any], 
        output_data: Dict[str, Any]
    ) -> str:
        """Save analysis to history"""
        try:
            history_entry = {
                "user_id": user_id,
                "input_data": input_data,
                "output_data": output_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("history").insert(history_entry).execute()
            
            if not response.data:
                raise Exception("Failed to save history")
            
            history_id = response.data[0]["id"]
            logger.info(f"History created: {history_id} for user: {user_id}")
            
            return history_id
            
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save analysis history"
            )
    
    async def get_user_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's analysis history"""
        try:
            response = (
                self.supabase.table("history")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return response.data
            
        except Exception as e:
            logger.error(f"Error fetching history: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch history"
            )
    
    async def delete_history(self, history_id: str, user_id: str) -> bool:
        """Delete a history item (only if owned by user)"""
        try:
            # Verify ownership
            check = (
                self.supabase.table("history")
                .select("*")
                .eq("id", history_id)
                .eq("user_id", user_id)
                .execute()
            )
            
            if not check.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="History not found or unauthorized"
                )
            
            # Delete
            self.supabase.table("history").delete().eq("id", history_id).execute()
            logger.info(f"History deleted: {history_id}")
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting history: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete history"
            )