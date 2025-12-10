# app/schemas/analyze_schema.py

from pydantic import BaseModel, Field, model_validator, PrivateAttr
from typing import Optional, Dict, Any, List


class AnalyzeRequest(BaseModel):
    """
    Request untuk analisis kimia - PURE CHATBOT MODE
    
    Mode 1: PROMPT ONLY (Chatbot AI)
    - User kirim pertanyaan natural language
    - AI jawab dengan rekomendasi lengkap
    
    Mode 2: PROPERTIES (Legacy/Advanced)
    - User kirim angka spesifik
    - AI analisis berdasarkan angka
    
    Mode 3: HYBRID (Optional)
    - Prompt + properties untuk context lebih kaya
    """
    
    # PRIMARY INPUT: Prompt (Natural Language)
    prompt: Optional[str] = Field(
        None, 
        description="Natural language question or request",
        min_length=3,
        max_length=2000,
        examples=[
            "Buatkan senyawa untuk anti-aging serum",
            "Saya butuh bahan aktif untuk brightening yang aman",
            "Rekomendasi preservative natural untuk cream"
        ]
    )
    
    # SECONDARY INPUT: Properties (Optional - for advanced users)
    titik_didih: Optional[float] = Field(None, ge=-273.15, description="Boiling point (°C)")
    viskositas: Optional[float] = Field(None, ge=0, description="Viscosity")
    stabilitas_termal: Optional[float] = Field(None, ge=0, le=100, description="Thermal stability (%)")
    kelarutan: Optional[float] = Field(None, ge=0, description="Solubility")
    
    # CONTEXT (Optional - untuk conversational AI)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    previous_compounds: Optional[List[str]] = Field(None, description="Previously discussed compounds")
    
    # NEW: Allow direct properties dict
    properties: Optional[Dict[str, Any]] = Field(None, description="Direct properties dictionary")
    
    @model_validator(mode='after')
    def validate_input(self):
        """
        Validasi fleksibel:
        - Jika ada prompt → VALID (mode chatbot)
        - Jika ada properties → VALID (mode legacy)
        - Jika ada properties dict → VALID
        - Jika keduanya kosong → ERROR
        """
        has_prompt = bool(self.prompt and self.prompt.strip())
        has_specific_props = any([
            self.titik_didih is not None,
            self.viskositas is not None,
            self.stabilitas_termal is not None,
            self.kelarutan is not None
        ])
        has_properties_dict = bool(self.properties and isinstance(self.properties, dict))
        
        if not has_prompt and not has_specific_props and not has_properties_dict:
            raise ValueError(
                "Please provide either:\n"
                "- 'prompt' (text question/request) for AI chatbot mode, OR\n"
                "- Physical properties (numbers) for analysis mode\n"
                "- 'properties' dictionary for direct specification"
            )
        
        return self
    
    class Config:
        json_schema_extra = {
            "examples": [
                # EXAMPLE 1: Pure Chatbot (Recommended for Frontend)
                {
                    "prompt": "Saya butuh bahan aktif untuk serum anti-aging yang cocok untuk kulit sensitif"
                },
                # EXAMPLE 2: Conversational dengan Context
                {
                    "prompt": "Bagaimana dengan alternatif yang lebih stabil?",
                    "conversation_id": "conv_123",
                    "previous_compounds": ["Ascorbic Acid"]
                },
                # EXAMPLE 3: Hybrid Mode
                {
                    "prompt": "Cari senyawa seperti ini tapi lebih stabil",
                    "stabilitas_termal": 90.0
                },
                # EXAMPLE 4: Legacy Mode (Pure Numbers)
                {
                    "titik_didih": 100.0,
                    "viskositas": 0.89,
                    "stabilitas_termal": 85.5,
                    "kelarutan": 12.3
                },
                # EXAMPLE 5: Properties Dictionary
                {
                    "properties": {
                        "boiling_point": 100.0,
                        "viscosity": 0.89,
                        "stability": 85.5
                    }
                }
            ]
        }


class ChemicalRecommendation(BaseModel):
    """Rekomendasi alternatif"""
    id: int
    name: str
    formula: str
    smiles: str
    properties: str  # String description (bukan dict, karena AI generate text)
    justification: str
    
    # Additional fields for better UX
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    price_range: Optional[str] = None
    availability: Optional[str] = None


class AnalyzeData(BaseModel):
    """Data hasil analisis - Conversational Format"""
    
    # CORE COMPOUND INFO
    formula: str = Field(..., description="Chemical formula")
    smiles: str = Field(..., description="SMILES notation")
    nama_senyawa: str = Field(..., description="Compound name")
    
    # PROPERTIES (flexible format)
    sifat_kimia: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chemical properties (numeric or descriptive)"
    )
    
    # AI EXPLANATION (conversational)
    justifikasi: str = Field(..., description="Why this compound is recommended")
    description: str = Field(..., description="Detailed explanation for user")
    
    # PRACTICAL GUIDANCE
    usage_guidelines: Optional[str] = Field(None, description="How to use this compound")
    dosage: Optional[str] = Field(None, description="Recommended dosage/concentration")
    
    # SAFETY
    safety_notes: Optional[str] = Field(None, description="Safety considerations")
    contraindications: Optional[List[str]] = Field(None, description="When NOT to use")
    
    # ALTERNATIVES
    recommendations: List[ChemicalRecommendation] = Field(
        default_factory=list,
        description="Alternative compounds"
    )
    
    # METADATA (optional)
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence (0-1)")
    sources: Optional[List[str]] = Field(None, description="Reference sources")
    
    # METADATA field (bukan _metadata)
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "source": "ml_service",
            "mode": "chatbot"
        },
        description="Internal metadata"
    )


class AnalyzeResponse(BaseModel):
    """Response dari endpoint /api/analyze"""
    success: bool
    message: str
    data: AnalyzeData
    history_id: str
    
    # Metadata untuk frontend
    conversation_id: Optional[str] = None
    processing_time: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Analysis completed successfully",
                "data": {
                    "formula": "C6H8O6",
                    "smiles": "OCC1OC(=O)C(O)=C1O",
                    "nama_senyawa": "Ascorbic Acid (Vitamin C)",
                    "sifat_kimia": {
                        "titik_didih": 192.0,
                        "stabilitas": "Moderate (requires stabilization)",
                        "kelarutan": "Highly water-soluble"
                    },
                    "justifikasi": "Vitamin C adalah antioksidan kuat yang sangat populer dalam produk anti-aging. Meskipun kurang stabil, formulasi modern dapat meningkatkan stabilitasnya.",
                    "description": "Ascorbic Acid bekerja dengan cara:\n1. Menetralisir radikal bebas\n2. Merangsang produksi kolagen\n3. Mencerahkan kulit\n\nCocok untuk serum dengan pH 3.5, disimpan dalam botol gelap.",
                    "usage_guidelines": "Aplikasikan 2x sehari (pagi & malam) setelah cleansing, sebelum moisturizer.",
                    "dosage": "Konsentrasi 10-20% untuk wajah. Mulai dari 10% jika kulit sensitif.",
                    "safety_notes": "Aman untuk penggunaan topikal. Patch test direkomendasikan untuk kulit sangat sensitif.",
                    "contraindications": ["Alergi terhadap Vitamin C", "Kulit yang sedang mengalami iritasi parah"],
                    "recommendations": [
                        {
                            "id": 1,
                            "name": "Sodium Ascorbyl Phosphate",
                            "formula": "C6H6Na3O9P",
                            "smiles": "C1C(C(C(C(O1)OP(=O)([O-])[O-])O)O)O.[Na+].[Na+]",
                            "properties": "Lebih stabil, pH netral (6-7), cocok untuk kulit sensitif",
                            "justification": "Bentuk stabil dari Vitamin C yang lebih gentle untuk kulit sensitif",
                            "pros": ["Stabil", "Cocok untuk kulit sensitif", "pH netral"],
                            "cons": ["Efektivitas sedikit lebih rendah", "Harga lebih mahal"],
                            "price_range": "Mid-range",
                            "availability": "Widely available"
                        }
                    ],
                    "confidence_score": 0.95,
                    "sources": ["PubMed", "Cosmetic Dermatology Journal"],
                    "metadata": {
                        "source": "ml_service",
                        "mode": "chatbot",
                        "rag_enabled": True
                    }
                },
                "history_id": "123e4567-e89b-12d3-a456-426614174000",
                "conversation_id": "conv_abc123",
                "processing_time": 2.5
            }
        }