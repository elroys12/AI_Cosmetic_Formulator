# ml_service/app/schemas.py

from pydantic import BaseModel, Field, PrivateAttr
from typing import Dict, Any, Optional, List


class SimpleMLRequest(BaseModel):
    """Simplified request for backward compatibility"""
    topic: Optional[str] = Field(None, description="Topic for analysis")
    prompt: Optional[str] = Field(None, description="Natural language prompt")
    properties: Optional[Dict[str, float]] = Field(None, description="Properties dictionary")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "anti-aging serum untuk kulit sensitif",
                "prompt": "Buatkan formula serum anti-aging",
                "properties": {"stabilitas_termal": 85.0}
            }
        }


class MLRequest(BaseModel):
    """
    Input untuk ML Service - PURE CHATBOT MODE
    
    PRIORITY 1: PROMPT (Natural Language)
    - User bertanya dalam bahasa natural
    - AI memahami intent dan generate rekomendasi
    
    PRIORITY 2: PROPERTIES (Numeric)
    - Legacy mode untuk advanced users
    - Analisis berdasarkan angka spesifik
    """
    
    # PRIMARY: Natural Language Input
    prompt: Optional[str] = Field(
        None,
        description="Natural language question/request from user",
        min_length=3,
        max_length=2000,
        examples=[
            "Buatkan senyawa untuk anti-aging",
            "Saya butuh preservative natural",
            "Alternatif Vitamin C yang lebih stabil"
        ]
    )
    
    # SECONDARY: Numeric Properties (Optional)
    properties: Optional[Dict[str, float]] = Field(
        None,
        description="Physical/chemical properties for analysis",
        examples=[{
            "titik_didih": 100.0,
            "viskositas": 0.89,
            "stabilitas_termal": 85.5,
            "kelarutan": 12.3
        }]
    )
    
    # CONTEXT for Conversational AI (Optional)
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Previous messages for context",
        examples=[[
            {"role": "user", "content": "Saya butuh serum anti-aging"},
            {"role": "assistant", "content": "Saya rekomendasikan Vitamin C..."},
            {"role": "user", "content": "Ada yang lebih stabil?"}
        ]]
    )
    
    previous_compounds: Optional[List[str]] = Field(
        None,
        description="Previously discussed compounds for reference",
        examples=[["Ascorbic Acid", "Retinol"]]
    )
    
    user_preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="User preferences (skin type, concerns, etc)",
        examples=[{
            "skin_type": "sensitive",
            "concerns": ["aging", "brightening"],
            "avoid_ingredients": ["parabens"]
        }]
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                # EXAMPLE 1: Pure Chatbot (Most Common)
                {
                    "prompt": "Saya butuh bahan aktif untuk mengatasi jerawat yang aman untuk kulit sensitif"
                },
                
                # EXAMPLE 2: Follow-up Question (dengan context)
                {
                    "prompt": "Bagaimana cara menggunakannya?",
                    "conversation_history": [
                        {"role": "user", "content": "Rekomendasi untuk jerawat?"},
                        {"role": "assistant", "content": "Niacinamide 5% sangat cocok..."}
                    ]
                },
                
                # EXAMPLE 3: Hybrid (Prompt + Properties)
                {
                    "prompt": "Cari senyawa seperti ini tapi yang lebih stabil",
                    "properties": {"stabilitas_termal": 90.0},
                    "previous_compounds": ["Ascorbic Acid"]
                },
                
                # EXAMPLE 4: Advanced dengan Preferences
                {
                    "prompt": "Rekomendasi moisturizer untuk kulit kering",
                    "user_preferences": {
                        "skin_type": "dry",
                        "budget": "affordable",
                        "preference": "natural ingredients"
                    }
                }
            ]
        }


class ChemicalRecommendation(BaseModel):
    """Alternative compound recommendation"""
    id: int
    name: str
    formula: str
    smiles: str
    properties: str  # Descriptive text (NOT dict)
    justification: str
    
    # Additional conversational fields
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    price_range: Optional[str] = None
    availability: Optional[str] = None


class MLPredictionData(BaseModel):
    """ML Prediction Result - Conversational Format"""
    
    # CORE INFO
    formula: str
    smiles: str
    nama_senyawa: str
    
    # PROPERTIES (flexible: dict or descriptive text)
    sifat_kimia: Dict[str, Any]
    
    # CONVERSATIONAL EXPLANATION
    justifikasi: str = Field(..., description="Why this compound?")
    description: str = Field(..., description="Detailed explanation in natural language")
    
    # HOW TO USE (New for chatbot)
    usage_guidelines: Optional[str] = Field(None, description="How to use this compound")
    dosage: Optional[str] = Field(None, description="Recommended dosage/concentration")
    
    # SAFETY
    safety_notes: Optional[str] = Field(None, description="Safety considerations")
    contraindications: Optional[List[str]] = Field(None, description="When NOT to use")
    
    # ALTERNATIVES
    recommendations: List[ChemicalRecommendation] = []
    
    # METADATA
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    sources: Optional[List[str]] = None
    
    # INTERNAL - Gunakan PrivateAttr untuk internal metadata
    _metadata: Dict[str, Any] = PrivateAttr(default_factory=lambda: {
        "source": "ml_service",
        "mode": "chatbot",
        "rag_enabled": False
    })


class MLResponse(BaseModel):
    """Response dari ML Service"""
    success: bool
    data: MLPredictionData
    
    # Metadata
    processing_time: Optional[float] = None
    model_version: str = "1.0.0"
    ai_model: str = "gemini-2.0-flash-exp"
    
    # Context (untuk conversational flow)
    conversation_id: Optional[str] = None
    requires_followup: Optional[bool] = Field(
        None,
        description="Does this response need clarification?"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "formula": "C3H7NO2",
                    "smiles": "CCC(=O)N",
                    "nama_senyawa": "Niacinamide (Vitamin B3)",
                    "sifat_kimia": {
                        "water_solubility": "Highly soluble",
                        "stability": "Very stable",
                        "pH_range": "5.0-7.0"
                    },
                    "justifikasi": "Niacinamide sangat cocok untuk kulit sensitif dengan jerawat karena sifatnya yang gentle namun efektif. Tidak menyebabkan iritasi dan dapat digunakan bersama bahan aktif lain.",
                    "description": "Niacinamide adalah bahan aktif multifungsi yang:\n\n1. **Mengurangi Jerawat**: Mengontrol produksi sebum dan mengurangi inflamasi\n2. **Aman untuk Sensitif**: Tidak mengiritasi, cocok untuk semua jenis kulit\n3. **Anti-Aging Bonus**: Meningkatkan elastisitas dan mencerahkan\n4. **Mudah Dikombinasi**: Bisa dipakai dengan AHA/BHA, retinol, vitamin C\n\nKonsentrasi ideal: 5% untuk kulit sensitif, bisa hingga 10% untuk hasil lebih cepat.",
                    "usage_guidelines": "Aplikasikan 2x sehari (pagi & malam) setelah toner, sebelum moisturizer. Tunggu 30 detik sebelum produk berikutnya.",
                    "dosage": "Konsentrasi 5-10% untuk wajah. Mulai dari 5% jika kulit sangat sensitif.",
                    "safety_notes": "Sangat aman. Efek samping minimal (kemerahan ringan di awal penggunaan, biasanya hilang dalam 1-2 minggu).",
                    "contraindications": ["Alergi terhadap vitamin B3 (sangat jarang)"],
                    "recommendations": [
                        {
                            "id": 1,
                            "name": "Azelaic Acid",
                            "formula": "C9H16O4",
                            "smiles": "C(CCCCCCCC(=O)O)C(=O)O",
                            "properties": "Antibakteri kuat, cocok untuk jerawat & rosacea",
                            "justification": "Alternatif yang lebih kuat untuk jerawat parah, tapi tetap gentle",
                            "pros": ["Sangat efektif untuk jerawat", "Anti-inflamasi", "Mencerahkan bekas jerawat"],
                            "cons": ["Bisa bikin kering di awal", "Tekstur agak gritty"],
                            "price_range": "Mid-range",
                            "availability": "Tersedia OTC (10%) atau resep dokter (15-20%)"
                        }
                    ],
                    "confidence_score": 0.95,
                    "sources": ["PubMed", "Cosmetic Dermatology Research"]
                },
                "processing_time": 2.3,
                "model_version": "1.0.0",
                "ai_model": "gemini-2.0-flash-exp",
                "conversation_id": "conv_abc123",
                "requires_followup": False
            }
        }