# app/schemas/history_schema.py

from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class HistoryItem(BaseModel):
    id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "input_data": {
                    "titik_didih": 100.0,
                    "viskositas": 0.89,
                    "stabilitas_termal": 85.5,
                    "kelarutan": 12.3
                },
                "output_data": {
                    "formula": "H2O",
                    "smiles": "O",
                    "sifat_kimia": {}
                },
                "created_at": "2024-11-18T10:30:00Z"
            }
        }


class HistoryListResponse(BaseModel):
    success: bool
    total: int
    data: List[HistoryItem]