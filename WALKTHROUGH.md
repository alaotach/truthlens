# TruthLens - Example Walkthrough

## System Demonstration

This document walks through a complete example of TruthLens analyzing a product.

## Example 1: Unrealistic Power Bank

### Input
```json
{
  "text": "20000mAh Quantum Power Bank with AI-powered charging technology. Charges your phone in just 2 minutes! 150W ultra-fast output. 100% efficiency guaranteed. Military-grade durability. Medical-grade safety. Price: $149.99"
}
```

### Processing Steps

#### 1. Product Data Extraction (`scraper.py`)
```python
ProductData(
    title="20000mAh Quantum Power Bank...",
    description="20000mAh Quantum Power Bank...",
    price=149.99,
    currency="USD",
    specs={
        'battery': '20000 mAh',
        'power': '150W'
    }
)
```

#### 2. Claim Extraction (`nlp_extractor.py`)
```python
Claims Found: 7
[
    Claim(text="20000mAh", category="battery_capacity", value=20000, unit="mAh"),
    Claim(text="Charges...2 minutes", category="charging_time", value=2, unit="minutes"),
    Claim(text="150W output", category="power_output", value=150, unit="W"),
    Claim(text="100% efficiency", category="efficiency", value=100, unit="%"),
    Claim(text="Quantum", category="marketing_buzzword"),
    Claim(text="AI-powered", category="marketing_buzzword"),
    Claim(text="Military-grade", category="marketing_buzzword"),
    Claim(text="Medical-grade", category="marketing_buzzword")
]
```

#### 3. Feasibility Verification (`feasibility.py`)

**Claim 1: 20000mAh Battery**
- Status: ✅ Feasible
- Confidence: 90%
- Reasoning: "20000mAh is within normal range for large power banks"

**Claim 2: Charges in 2 minutes**
- Status: ❌ Impossible
- Confidence: 95%
- Reasoning: "Charging in 2 minutes is physically impossible. Even with highest charging rates, battery chemistry requires minimum time."
- Technical: "Current technology: minimum ~15-30 minutes for fast charge"

**Claim 3: 150W Output**
- Status: ⚠️ Exaggerated
- Confidence: 85%
- Reasoning: "150W exceeds USB Power Delivery standard (100W max). Likely marketing exaggeration."
- Technical: "Portable devices limited to 100W due to battery constraints"

**Claim 4: 100% Efficiency**
- Status: ❌ Impossible
- Confidence: 100%
- Reasoning: "100% efficiency violates laws of thermodynamics. All real devices lose energy as heat."
- Technical: "Second law of thermodynamics: no process can be 100% efficient"

**Claim 5-8: Buzzwords (Quantum, AI, Military/Medical-grade)**
- Status: ⚠️ Exaggerated
- Confidence: 75-90%
- Reasoning: Marketing hype without scientific basis or regulatory approval

#### 4. Price Analysis (`pricing.py`)

```python
Category: power_bank
Base Price Calculation:
  - Base cost: $10
  - Capacity value: 20000mAh × $0.02 = $400
  - Power output value: 150W × $0.50 = $75
  - Total spec value: $485

Fair Price Range: $60 - $120
Market Average: $90
Listed Price: $149.99

Overpricing: +66.7%
Verdict: highly_overpriced
```

#### 5. Scoring (`scoring.py`)

**Reality Score Calculation:**
```
Feasible claims: 1 (20000mAh) → 100 points × 0.9 weight = 90
Exaggerated claims: 5 (150W, buzzwords) → 50 points × avg 0.8 weight = 200
Impossible claims: 2 (2min charge, 100% eff) → 0 points × avg 0.95 weight = 0

Total: 290 / Total Weight: 7.55 = 38.4/100
Reality Score: 38.4
```

**Pricing Score Calculation:**
```
Verdict: highly_overpriced → 15.0/100
Pricing Score: 15.0
```

**Overall Verdict:**
- Impossible claims detected → "not_recommended"

### Final Output

```json
{
  "product_title": "20000mAh Quantum Power Bank...",
  "reality_score": 38.4,
  "pricing_score": 15.0,
  "overall_verdict": "not_recommended",
  "summary": "This product makes technically impossible claims. Not recommended. Many claims appear exaggerated or unfeasible. Pricing is higher than justified by features.",
  "red_flags": [
    "❌ Impossible claim: Charging in 2 minutes",
    "❌ Impossible claim: 100% efficiency",
    "⚠️ Multiple exaggerated claims detected (5 found)",
    "💰 Overpriced by 66.7% compared to market average",
    "📢 Heavy use of marketing buzzwords without substantiation"
  ],
  "recommendations": [
    "🔍 Verify claims with independent reviews",
    "💵 Consider alternatives in $60-$120 range",
    "🚫 Avoid this product - impossible claims indicate unreliable seller"
  ]
}
```

---

## Example 2: Realistic Product

### Input
```json
{
  "text": "Portable 5000mAh Power Bank. 18W Fast Charging. Charges in 90 minutes via USB-C. Lightweight at 150g. Dual output ports. Price: $29.99"
}
```

### Analysis Result

**Claims Found:** 4 verified claims

**Verifications:**
- ✅ 5000mAh capacity - Feasible (90% confidence)
- ✅ 18W output - Feasible (90% confidence)  
- ✅ 90 minute charging - Feasible (95% confidence)
- ✅ 150g weight - Feasible (85% confidence)

**Price Analysis:**
- Fair range: $25-$40
- Market average: $32
- Overpricing: -6.5% (good value!)
- Verdict: excellent_value

**Scores:**
- Reality Score: 89.5/100
- Pricing Score: 100/100
- Overall Verdict: good_value

**Summary:** "This product appears to be good value with realistic claims and fair pricing. Product claims are largely credible. Pricing is fair or better than average."

**Red Flags:** ✅ No major red flags detected

**Recommendations:**
- 👍 Price is fair - good time to buy
- ✨ Product appears legitimate - read user reviews to confirm

---

## System Architecture Flow

```
User Input (URL/Text)
    ↓
[ProductScraper] → Extract title, price, specs, description
    ↓
[ClaimExtractor] → Identify 7 types of claims + buzzwords
    ↓
[FeasibilityEngine] → Verify each claim (feasible/exaggerated/impossible)
    ↓
[PricingEngine] → Calculate fair price range, compare to market
    ↓
[ScoringEngine] → Generate scores, verdict, recommendations
    ↓
JSON Response to Frontend
    ↓
[React UI] → Visual display with scores, flags, recommendations
```

---

## Rule Engine Design

### Feasibility Rules (Physics-Based)

#### Battery Capacity
```python
if capacity > 100,000 mAh:
    return IMPOSSIBLE  # Too large for portable
elif capacity > 50,000 mAh:
    return EXAGGERATED  # Unusually high
elif capacity >= 1,000 mAh:
    return FEASIBLE
```

#### Charging Time
```python
if time < 5 minutes:
    return IMPOSSIBLE  # Battery chemistry limits
elif time < 15 minutes:
    return EXAGGERATED  # Aggressive, likely unsafe
elif time < 30 minutes:
    return FEASIBLE  # Fast charge tech
else:
    return FEASIBLE  # Normal
```

#### Power Output
```python
if power > 150W:
    return IMPOSSIBLE  # Exceeds portable limits
elif power > 100W:
    return EXAGGERATED  # Exceeds USB-PD standard
elif power > 18W:
    return FEASIBLE  # Fast charging
else:
    return FEASIBLE  # Standard
```

#### Efficiency
```python
if efficiency >= 100:
    return IMPOSSIBLE  # Violates thermodynamics
elif efficiency > 98:
    return IMPOSSIBLE  # Not achievable in practice
elif efficiency > 95:
    return EXAGGERATED  # Very optimistic
elif efficiency >= 70:
    return FEASIBLE
```

### Pricing Rules (Market-Based)

```python
category_benchmarks = {
    'power_bank': {
        'price_per_mah': 0.02,  # $0.02/mAh
        'base_price': 10,
        'brand_premium': 1.3
    }
}

fair_price = base_price + (capacity × price_per_mah) + (power × price_per_watt)
fair_range = (fair_price × 0.8, fair_price × brand_premium)

if listed_price < fair_min:
    verdict = "excellent_value"
elif listed_price <= fair_max:
    verdict = "fair"
elif overpricing <= 25%:
    verdict = "slightly_overpriced"
else:
    verdict = "overpriced"
```

---

## Extensibility

### Adding New Product Categories

1. **Add category patterns** in `nlp_extractor.py`:
```python
self.claim_patterns['new_category'] = {
    'patterns': [r'pattern1', r'pattern2'],
    'unit': 'unit_name',
    'keywords': ['keyword1', 'keyword2']
}
```

2. **Add feasibility rules** in `feasibility.py`:
```python
def _verify_new_category(self, claim):
    # Physics/engineering constraints
    if value > max_theoretical:
        return IMPOSSIBLE
    # ... more rules
```

3. **Add pricing benchmarks** in `pricing.py`:
```python
self.category_benchmarks['new_category'] = {
    'base_price': X,
    'brand_premium': Y,
    'typical_range': (min, max)
}
```

### Future Enhancements

1. **ML Integration** (without replacing rules):
   - Train claim classifier on labeled data
   - Use as additional input to rule engine
   - Rules provide explainability, ML adds coverage

2. **User Feedback Loop**:
   - Collect user votes on accuracy
   - Adjust confidence scores over time
   - Flag controversial claims for review

3. **Historical Price Tracking**:
   - Store price history in database
   - Detect price drop patterns
   - Alert users to good deals

4. **Browser Extension**:
   - Inject analysis directly on product pages
   - One-click analysis from any e-commerce site
   - Real-time pricing comparison

5. **Multi-language Support**:
   - Translate claim patterns for other languages
   - Localize pricing benchmarks by region
   - Support international e-commerce sites

---

## Production Deployment Notes

### Scalability Considerations

1. **Caching**: Cache analysis results for identical products
2. **Rate Limiting**: Prevent abuse of analysis endpoint
3. **Async Processing**: Queue long-running scraping tasks
4. **Database**: Store benchmarks, historical data, user feedback
5. **CDN**: Serve frontend from CDN for global performance

### Security

1. **Input Validation**: Sanitize URLs and text inputs
2. **Rate Limiting**: Per-IP and per-user limits
3. **CORS**: Restrict to known frontend domains
4. **API Keys**: Optional authentication for heavy users

### Monitoring

1. **Logging**: Track analysis requests, failures, response times
2. **Metrics**: Success rate, average scores, popular categories
3. **Alerts**: Monitor for system errors or suspicious patterns
