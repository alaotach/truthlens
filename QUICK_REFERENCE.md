# TruthLens - Quick Reference

## 🚀 Quick Start Commands

### Start Backend
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
```
→ http://localhost:8000

### Start Frontend
```bash
cd frontend && npm run dev
```
→ http://localhost:5173

### Test API
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"YOUR_PRODUCT_TEXT_HERE"}'
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/analyze` | POST | Full product analysis |
| `/api/v1/extract-claims` | POST | Extract claims only |
| `/docs` | GET | Swagger UI |

---

## 🎯 Claim Categories

1. **battery_capacity** - mAh values
2. **charging_time** - minutes/hours
3. **power_output** - Watts
4. **efficiency** - percentage
5. **speed** - km/h, mph
6. **range** - kilometers, miles
7. **weight** - kg, grams
8. **capacity_storage** - GB, TB, liters
9. **marketing_buzzword** - AI, quantum, medical-grade, etc.
10. **comparative** - "2x faster", "best in market"

---

## ✅ Verification Statuses

- **feasible** 🟢 - Technically possible and reasonable
- **exaggerated** 🟡 - Possible but unlikely or requires conditions
- **impossible** 🔴 - Violates physics/engineering constraints

---

## 💰 Price Verdicts

1. **excellent_value** - Below fair price range
2. **fair** - Within fair price range
3. **slightly_overpriced** - 10-25% above fair value
4. **overpriced** - 25-50% above fair value
5. **highly_overpriced** - >50% above fair value

---

## 🎨 Overall Verdicts

- **good_value** ✅ - Good claims + fair price
- **acceptable** ⚠️ - Mixed results
- **overpriced** 💰 - Fair claims but expensive
- **misleading_claims** ⚠️ - Many exaggerated claims
- **not_recommended** ❌ - Impossible claims detected

---

## 📊 Score Interpretation

### Reality Score
- **80-100**: Highly credible claims
- **60-79**: Some concerns, verify details
- **40-59**: Many questionable claims
- **0-39**: Serious red flags, avoid

### Pricing Score
- **80-100**: Fair or excellent price
- **60-79**: Slightly high but acceptable
- **40-59**: Overpriced
- **0-39**: Significantly overpriced

---

## 🔧 Common Tasks

### Add New Product Category
1. Update `nlp_extractor.py` - add patterns
2. Update `feasibility.py` - add verification rules
3. Update `pricing.py` - add pricing benchmarks

### Modify Price Thresholds
Edit `pricing.py`:
```python
self.category_benchmarks['category_name'] = {
    'price_per_unit': X,
    'base_price': Y,
    'brand_premium': Z
}
```

### Adjust Physics Constraints
Edit `feasibility.py`:
```python
self.constraints['claim_type'] = {
    'typical_range': (min, max),
    'max_reasonable': limit
}
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules
npm install
```

### CORS errors
Check `backend/app/main.py`:
```python
allow_origins=["http://localhost:5173"]
```

### Module not found
Make sure you're in virtual environment:
```bash
source backend/venv/bin/activate
```

---

## 📁 File Locations

### Key Backend Files
- `backend/app/core/feasibility.py` - Physics rules
- `backend/app/core/pricing.py` - Price benchmarks
- `backend/app/core/nlp_extractor.py` - Claim patterns
- `backend/app/models/schemas.py` - Data models

### Key Frontend Files
- `frontend/src/App.jsx` - Main app
- `frontend/src/components/ResultCard.jsx` - Results UI
- `frontend/src/services/api.js` - API client

---

## 🧪 Test Examples

### Realistic Product (should pass)
```json
{
  "text": "5000mAh portable charger. 18W fast charging. Lightweight 150g design. Price: $29.99"
}
```

### Unrealistic Product (should fail)
```json
{
  "text": "20000mAh Quantum AI battery. Charges in 2 minutes! 100% efficiency guaranteed. Military-grade. $199"
}
```

---

## 📖 Documentation

- **README.md** - Main project overview
- **PROJECT_SUMMARY.md** - Complete implementation details
- **WALKTHROUGH.md** - Example analysis walkthrough
- **backend/README.md** - Backend API docs
- **frontend/README.md** - Frontend component docs

---

## 🎓 Development Workflow

1. **Make changes** to backend/frontend
2. **Test locally** with curl or UI
3. **Check logs** in terminal
4. **Update tests** if needed
5. **Document** changes in relevant README

---

## 🚢 Production Deployment Checklist

- [ ] Set proper CORS origins
- [ ] Add rate limiting
- [ ] Enable HTTPS
- [ ] Set up database for caching
- [ ] Add monitoring/logging
- [ ] Optimize frontend build
- [ ] Configure CDN
- [ ] Set environment variables
- [ ] Add error tracking (Sentry)
- [ ] Set up CI/CD

---

**For more details, see PROJECT_SUMMARY.md and WALKTHROUGH.md**
