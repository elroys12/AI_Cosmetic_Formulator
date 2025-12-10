# app/routers/history.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.history_schema import HistoryListResponse
from app.services.history_service import HistoryService
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=HistoryListResponse)
async def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get user's analysis history
    
    Returns list of past chemical analyses with input and output data.
    """
    history_service = HistoryService()
    history_data = await history_service.get_user_history(
        user_id=current_user["id"],
        limit=limit
    )
    
    return {
        "success": True,
        "total": len(history_data),
        "data": history_data
    }


@router.delete("/{history_id}")
async def delete_history(
    history_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a history item
    
    Only the owner can delete their history.
    """
    history_service = HistoryService()
    await history_service.delete_history(history_id, current_user["id"])
    
    return {
        "success": True,
        "message": "History deleted successfully"
    }