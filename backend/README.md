# TruthLens Backend

FastAPI backend for TruthLens - Product Reality & Fair Price Checker

## Quick Start

### 1. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Main Endpoints

### POST /api/v1/analyze
Analyze a product from URL or text description

**Request:**
```json
{
  "url": "https://example.com/product",
  "text": "10000mAh power bank charges in 5 minutes"
}
```

**Response:**
```json
{
  "product_title": "...",
  "claims_found": [...],
  "verifications": [...],
  "price_analysis": {...},
  "reality_score": 75.5,
  "pricing_score": 80.0,
  "overall_verdict": "good_value",
  "summary": "...",
  "red_flags": [...],
  "recommendations": [...]
}
```

## Architecture

```
app/
├── main.py              # FastAPI app entry point
├── api/
│   └── routes.py        # API endpoints
├── core/
│   ├── scraper.py       # Product data extraction
│   ├── nlp_extractor.py # Claim extraction
│   ├── feasibility.py   # Physics/engineering verification
│   ├── pricing.py       # Price analysis
│   └── scoring.py       # Final scoring logic
└── models/
    └── schemas.py       # Pydantic models
```

## Core Modules

### Scraper (`scraper.py`)
- Extracts product data from URLs or text
- Handles Amazon, Flipkart-like structures
- Parses specs, price, and descriptions

### NLP Extractor (`nlp_extractor.py`)
- Identifies product claims using pattern matching
- Extracts performance metrics (battery, power, speed, etc.)
- Flags marketing buzzwords

### Feasibility Engine (`feasibility.py`)
- Validates claims against physics/engineering rules
- Checks battery capacity limits
- Verifies charging time feasibility
- Evaluates power output claims
- Detects impossible efficiency values

### Pricing Engine (`pricing.py`)
- Compares prices to market benchmarks
- Calculates fair price ranges
- Determines overpricing percentage

### Scoring Engine (`scoring.py`)
- Generates reality score (0-100)
- Calculates pricing fairness score
- Produces overall verdict
- Generates recommendations

## Testing

Run tests:
```bash
pytest tests/ -v
```

## Environment Variables

Create `.env` file:
```
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```
