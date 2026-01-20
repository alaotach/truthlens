"""
Pydantic models for request/response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProductInput(BaseModel):
    """Input from user - either URL or raw text"""
    url: Optional[str] = None
    text: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/product/xyz",
                "text": "10000mAh power bank that charges in 5 minutes"
            }
        }


class ProductData(BaseModel):
    """Extracted product information"""
    title: str
    description: str
    price: Optional[float] = None
    currency: str = "USD"
    specs: Dict[str, Any] = Field(default_factory=dict)
    raw_text: str


class Claim(BaseModel):
    """Individual product claim"""
    text: str
    category: str  # power, capacity, speed, range, efficiency, etc.
    extracted_value: Optional[float] = None
    unit: Optional[str] = None


class ClaimVerification(BaseModel):
    """Verification result for a single claim"""
    claim: str
    status: str  # feasible, exaggerated, impossible
    confidence: float  # 0-1
    reasoning: str
    technical_details: Optional[str] = None
    flags: List[str] = Field(default_factory=list)  # Additional flags like 'high_capacity', 'impossible', etc.


class PriceAnalysis(BaseModel):
    """Price fairness analysis"""
    listed_price: float
    fair_price_min: float
    fair_price_max: float
    market_average: float
    overpricing_percentage: float
    verdict: str  # fair, slightly_overpriced, overpriced, excellent_value


class ProductAnalysis(BaseModel):
    """Complete analysis result"""
    product_title: str
    claims_found: List[Claim]
    verifications: List[ClaimVerification]
    price_analysis: Optional[PriceAnalysis] = None
    reality_score: float  # 0-100
    pricing_score: float  # 0-100
    overall_verdict: str  # good_value, overpriced, misleading_claims, not_recommended
    summary: str
    red_flags: List[str]
    recommendations: List[str]


class HealthCheck(BaseModel):
    """API health check response"""
    status: str
    version: str
