# app/models/history.py

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class HistoryInDB(BaseModel):
    id: str
    user_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    created_at: datetime