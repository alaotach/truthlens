# TruthLens - AI-Powered Product Reality & Fair Price Checker

## Overview

TruthLens helps consumers make informed purchasing decisions by:
- Verifying product claims against physics and engineering constraints
- Analyzing price fairness compared to market benchmarks
- Providing simple, actionable insights

## Architecture

### Backend (Python + FastAPI)
- **Scraper Module**: Extracts product data from URLs or text
- **NLP Engine**: Identifies and structures product claims
- **Feasibility Engine**: Validates claims using rule-based physics/engineering checks
- **Pricing Engine**: Compares prices against market data
- **Scoring Engine**: Generates reality and pricing scores

### Frontend (React + Tailwind CSS)
- Clean, minimal interface
- Real-time analysis feedback
- Mobile-responsive design

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend will run at `http://localhost:8000`

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://localhost:5173`

## Usage

### Analyzing Products

**Method 1: Product Description Text (Recommended)**
- Paste product title, description, specs, and price
- Most reliable method
- Works with any product

**Method 2: Product URL**
- Demo URLs provided for testing (example.com)
- Real e-commerce URLs may be limited by anti-bot protections
- For best results with live sites, copy-paste product text instead

### Demo URLs
- `https://example.com/product/realistic-powerbank` - Good product example
- `https://example.com/product/unrealistic-quantum-battery` - Bad product example

Frontend will run at `http://localhost:5173`

## System Flow

1. User provides product URL or description
2. System extracts product details (title, specs, claims, price)
3. NLP engine identifies specific claims
4. Feasibility engine validates each claim
5. Pricing engine checks fair market value
6. Results presented with scores and recommendations

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, spaCy, BeautifulSoup4
- **Frontend**: React 18, Vite, Tailwind CSS, Axios
- **Testing**: Pytest, React Testing Library

## Project Structure

```
truthlens/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Business logic modules
│   │   └── models/   # Pydantic schemas
│   └── tests/
├── frontend/         # React frontend
│   └── src/
│       ├── components/
│       ├── services/
│       └── App.jsx
└── README.md
```

## Scalability

- Modular architecture allows easy addition of new product categories
- Rule engine can be extended with new feasibility checks
- API-first design enables browser extension, mobile app integration
- Can add ML models for advanced claim detection without affecting core logic

## Future Enhancements

- Browser extension for inline product page analysis
- Mobile app (React Native)
- User voting/feedback system for claim accuracy
- Historical price tracking
- Multi-language support
- Advanced ML for context-aware claim detection

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details
