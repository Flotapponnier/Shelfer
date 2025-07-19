from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ProductUploadRequest(BaseModel):
    filename: str
    content_type: str

class ProductImprovement(BaseModel):
    category: str
    priority: str
    current: str
    suggested: str
    impact: str

class ProductAnalysisResponse(BaseModel):
    overall_score: int
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[ProductImprovement]
    seo_recommendations: List[str]
    missing_fields: List[str]
    conversion_tips: List[str]
    analysis: Optional[str] = None
    error: Optional[str] = None

class SchemaOrgProduct(BaseModel):
    context: str = "https://schema.org/"
    type: str
    id: Optional[str] = None
    name: str
    url: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[Dict[str, Any]] = None
    offers: Optional[Dict[str, Any]] = None
    image: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None