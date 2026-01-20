"""
API routes for TruthLens
"""
import hashlib
import json
from functools import lru_cache
from fastapi import APIRouter, HTTPException
from app.models.schemas import ProductInput, ProductAnalysis, HealthCheck
from app.core.scraper import ProductScraper
from app.core.nlp_extractor import ClaimExtractor
from app.core.feasibility import FeasibilityEngine
from app.core.pricing import PricingEngine
from app.core.scoring import ScoringEngine

router = APIRouter()

# Initialize core modules (singleton instances for caching)
scraper = ProductScraper()
claim_extractor = ClaimExtractor()
feasibility_engine = FeasibilityEngine()
pricing_engine = PricingEngine()
scoring_engine = ScoringEngine()

# Simple in-memory cache for analysis results
_analysis_cache = {}


@router.get("/health", response_model=HealthCheck)
async def health():
    """Health check endpoint"""
    return HealthCheck(status="healthy", version="1.0.0")


@router.post("/analyze", response_model=ProductAnalysis)
async def analyze_product(product_input: ProductInput):
    """
    Analyze a product from URL or text description
    
    Returns complete analysis with:
    - Extracted claims
    - Feasibility verification
    - Price analysis
    - Scores and verdict
    
    Uses caching for repeated requests
    """
    try:
        # Input validation
        if not product_input.url and not product_input.text:
            raise HTTPException(
                status_code=400,
                detail="❌ Either 'url' or 'text' must be provided. Please enter product details."
            )
        
        if product_input.url and product_input.text:
            raise HTTPException(
                status_code=400,
                detail="⚠️ Provide either URL or text, not both."
            )
        
        if product_input.text and len(product_input.text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="❌ Product description too short. Please provide at least 10 characters."
            )
        
        if product_input.text and len(product_input.text) > 10000:
            raise HTTPException(
                status_code=400,
                detail="⚠️ Product description too long. Please limit to 10,000 characters."
            )
        
        # Generate cache key from input
        if product_input.url:
            cache_key = hashlib.md5(product_input.url.encode()).hexdigest()
        else:
            # Use first 500 chars for cache key
            cache_key = hashlib.md5(product_input.text[:500].encode()).hexdigest()
        
        # Check cache with FIFO eviction
        if cache_key in _analysis_cache:
            return _analysis_cache[cache_key]
        
        # Evict oldest if cache is full
        if len(_analysis_cache) >= 100:
            # Remove first (oldest) item
            first_key = next(iter(_analysis_cache))
            del _analysis_cache[first_key]
        
        # Step 1: Extract product data
        if product_input.url:
            product_data = scraper.extract_from_url(product_input.url)
        else:
            product_data = scraper.extract_from_text(product_input.text)
        
        # Step 2: Extract claims using NLP
        claims = claim_extractor.extract_claims(product_data)
        
        # Step 3: Verify claim feasibility
        verifications = feasibility_engine.verify_claims(claims)
        
        # Step 4: Analyze pricing
        price_analysis = pricing_engine.analyze_price(product_data, claims)
        
        # Step 5: Generate scores and final analysis
        analysis = scoring_engine.generate_analysis(
            product_data,
            claims,
            verifications,
            price_analysis
        )
        
        # Cache result
        _analysis_cache[cache_key] = analysis
        
        # Limit cache size
        if len(_analysis_cache) > 100:
            # Remove oldest entry (simple FIFO)
            _analysis_cache.pop(next(iter(_analysis_cache)))
        
        return analysis
    
    except ValueError as e:
        # User-friendly errors from scraper
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/extract-claims")
async def extract_claims_only(product_input: ProductInput):
    """
    Extract claims from product without full analysis
    Useful for debugging or partial analysis
    """
    try:
        if product_input.url:
            product_data = scraper.extract_from_url(product_input.url)
        elif product_input.text:
            product_data = scraper.extract_from_text(product_input.text)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'url' or 'text' must be provided"
            )
        
        claims = claim_extractor.extract_claims(product_data)
        
        return {
            "product_title": product_data.title,
            "claims": claims,
            "count": len(claims)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Claim extraction failed: {str(e)}"
        )


@router.post("/verify-claim")
async def verify_single_claim(claim_text: str):
    """
    Verify a single claim (for testing/debugging)
    """
    try:
        from app.models.schemas import Claim
        
        # Create a claim object from text
        claim = Claim(
            text=claim_text,
            category='unknown',
            extracted_value=None,
            unit=None
        )
        
        # Try to extract value from text
        import re
        numbers = re.findall(r'\d+\.?\d*', claim_text)
        if numbers:
            claim.extracted_value = float(numbers[0])
        
        # Verify
        verification = feasibility_engine._verify_single_claim(claim)
        
        return verification
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )
