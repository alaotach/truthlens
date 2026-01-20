"""
Pricing intelligence module
Analyzes product pricing fairness against market benchmarks
"""
from typing import Dict, Optional, List, Tuple
from app.models.schemas import PriceAnalysis, ProductData, Claim


class PricingEngine:
    """
    Analyzes product pricing fairness
    Uses market data, category benchmarks, and depreciation logic
    """
    
    def __init__(self):
        # Exchange rates (updated for accuracy - Jan 2026)
        self.exchange_rates = {
            'USD': 1.0,
            'INR': 0.012,  # 1 INR ≈ 0.012 USD (₹83 = $1)
            'EUR': 1.09,
            'GBP': 1.27
        }
        
        # Market benchmark database (in USD equivalent)
        self.category_benchmarks = {
            'power_bank': {
                'price_per_mah': {
                    'budget': 0.001,    # $0.001 per mAh for budget brands
                    'mid_range': 0.0015, # $0.0015 per mAh for mid-range
                    'premium': 0.003,   # $0.003 per mAh for premium brands
                },
                'base_price': 8,  # Base manufacturing cost
                'brand_premium': 1.5,  # 50% brand markup acceptable
                'typical_range': (10, 80),
                'fast_charge_premium': 1.2,  # 20% more for fast charging
                'pd_premium': 1.3,  # 30% more for USB-C PD
                'wireless_premium': 1.25,  # 25% more for wireless
                'display_premium': 1.15,  # 15% more for LED display
            },
            'charger': {
                'price_per_watt': {
                    'budget': 0.25,     # $0.25 per watt
                    'mid_range': 0.4,   # $0.40 per watt
                    'premium': 0.7,     # $0.70 per watt (GaN chargers)
                },
                'base_price': 5,
                'brand_premium': 1.4,
                'typical_range': (10, 60),
                'gan_premium': 1.4,  # 40% more for GaN technology
                'multi_port_premium': 1.2,  # 20% more per additional port
            },
            'cable': {
                'base_price': 3,
                'length_factor': 1.2,  # 20% more per meter
                'certified_premium': 1.5,  # MFi, USB-IF certified
                'typical_range': (5, 30),
            },
            'battery': {
                'price_per_mah': 0.002,  # Replacement batteries
                'base_price': 10,
                'oem_premium': 2.0,  # OEM vs third-party
                'typical_range': (15, 100),
            },
            'electronics': {
                'base_price': 20,
                'brand_premium': 1.5,
                'typical_range': (30, 500),
            },
            'gadget': {
                'base_price': 15,
                'brand_premium': 1.4,
                'typical_range': (20, 300),
            }
        }
        
        # Pricing red flags
        self.price_red_flags = {
            'excessive_markup': 2.5,  # >250% of fair value
            'brand_premium_limit': 2.0,  # >200% brand markup is suspicious
            'suspiciously_cheap': 0.5,  # <50% of fair value (fake/counterfeit risk)
            'normal_variance': 0.2,  # ±20% is normal market variance
        }
        
        # Brand recognition for pricing (helps determine if premium is justified)
        self.premium_brands = [
            'anker', 'belkin', 'aukey', 'ravpower', 'samsung',
            'apple', 'google', 'xiaomi', 'oneplus', 'realme'
        ]
        self.budget_brands = [
            'ambrane', 'syska', 'portronics', 'mi', 'redmi',
            'boat', 'ptron', 'generic', 'unbranded'
        ]
    
    def analyze_price(
        self,
        product_data: ProductData,
        claims: List[Claim]
    ) -> Optional[PriceAnalysis]:
        """
        Analyze if product price is fair
        Returns PriceAnalysis or None if price not available
        """
        if product_data.price is None or product_data.price <= 0:
            return None
        
        # Convert price to USD for comparison
        currency = product_data.currency or 'USD'
        rate = self.exchange_rates.get(currency, 1.0)
        price_usd = product_data.price * rate
        
        # Determine product category
        category = self._determine_category(product_data, claims)
        
        # Calculate fair price based on specs and category (in USD)
        fair_price_min, fair_price_max = self._calculate_fair_price_range(
            product_data, claims, category
        )
        
        # Get market average
        market_avg = (fair_price_min + fair_price_max) / 2
        
        # Calculate overpricing percentage using USD-normalized price
        overpricing = ((price_usd - market_avg) / market_avg) * 100
        
        # Determine verdict using normalized price
        verdict = self._determine_price_verdict(
            price_usd, fair_price_min, fair_price_max, overpricing
        )
        
        return PriceAnalysis(
            listed_price=product_data.price,
            fair_price_min=round(fair_price_min, 2),
            fair_price_max=round(fair_price_max, 2),
            market_average=round(market_avg, 2),
            overpricing_percentage=round(overpricing, 1),
            verdict=verdict
        )
    
    def _determine_category(
        self, product_data: ProductData, claims: List[Claim]
    ) -> str:
        """Determine product category from data and claims"""
        text = (product_data.title + ' ' + product_data.description).lower()
        
        # Check for category keywords
        if any(word in text for word in ['power bank', 'powerbank', 'portable charger']):
            return 'power_bank'
        elif any(word in text for word in ['charger', 'adapter', 'charging']):
            return 'charger'
        elif any(word in text for word in ['electronics', 'gadget', 'device']):
            return 'electronics'
        else:
            return 'gadget'
    
    def _calculate_fair_price_range(
        self,
        product_data: ProductData,
        claims: List[Claim],
        category: str
    ) -> Tuple[float, float]:
        """
        Calculate fair price range based on specs and category
        """
        benchmark = self.category_benchmarks.get(
            category,
            self.category_benchmarks['gadget']
        )
        
        # Base calculation
        base_price = benchmark['base_price']
        
        # Add value based on specs from claims
        spec_value = self._calculate_spec_value(claims, category)
        
        # Calculate fair price
        fair_price = base_price + spec_value
        
        # Apply reasonable range
        min_price = fair_price * 0.8  # 20% below fair
        max_price = fair_price * benchmark['brand_premium']  # Brand premium
        
        # Ensure within category typical range
        category_min, category_max = benchmark['typical_range']
        min_price = max(min_price, category_min)
        max_price = min(max_price, category_max)
        
        return (min_price, max_price)
    
    def _calculate_spec_value(self, claims: List[Claim], category: str) -> float:
        """Calculate additional value based on specifications"""
        value = 0.0
        benchmark = self.category_benchmarks.get(category, {})
        
        # Detect brand tier from product text
        brand_tier = 'mid_range'  # default
        
        for claim in claims:
            if claim.extracted_value is None:
                continue
            
            # Power bank capacity pricing
            if claim.category == 'battery_capacity' and category == 'power_bank':
                price_per_mah = benchmark.get('price_per_mah', {})
                if isinstance(price_per_mah, dict):
                    rate = price_per_mah.get(brand_tier, 0.0015)
                else:
                    rate = 0.0015  # fallback for old format
                value += claim.extracted_value * rate
                
                # Add premiums for features
                if 'fast_charge_premium' in benchmark:
                    # Check if fast charging claimed
                    has_fast_charge = any(c.category == 'power_output' and c.extracted_value and c.extracted_value > 18 for c in claims)
                    if has_fast_charge:
                        value *= benchmark['fast_charge_premium']
            
            # Power output pricing
            elif claim.category == 'power_output':
                if category == 'charger':
                    price_per_watt = benchmark.get('price_per_watt', {})
                    if isinstance(price_per_watt, dict):
                        rate = price_per_watt.get(brand_tier, 0.4)
                    else:
                        rate = 0.4
                    value += claim.extracted_value * rate
                else:
                    value += claim.extracted_value * 0.3
            
            # High efficiency adds value
            elif claim.category == 'efficiency' and claim.extracted_value > 85:
                value += 5  # Premium for high efficiency
            
            # Fast charging adds value
            elif claim.category == 'charging_time':
                if claim.unit == 'time' and claim.extracted_value:
                    # Extract minutes
                    minutes = claim.extracted_value
                    if 'hour' in claim.text.lower():
                        minutes *= 60
                    # Fast charge if under 2 hours (120 min)
                    if minutes < 120:
                        value += 8
            
            # Charge cycles add value
            elif claim.category == 'charge_cycles' and claim.extracted_value > 500:
                value += 5  # Premium for longevity
            
            # Good warranty adds value
            elif claim.category == 'warranty' and claim.extracted_value >= 12:
                value += 3  # Warranty coverage value
        
        return value
    
    def _determine_price_verdict(
        self,
        listed_price: float,
        fair_min: float,
        fair_max: float,
        overpricing_pct: float
    ) -> str:
        """Determine pricing verdict with more nuanced categories"""
        
        # Suspiciously cheap - possible counterfeit
        if listed_price < fair_min * 0.6:
            return 'suspiciously_cheap'
        # Great value
        elif listed_price < fair_min:
            return 'excellent_value'
        # Fair price range
        elif listed_price <= fair_max:
            if listed_price <= (fair_min + fair_max) / 2:
                return 'good_value'
            else:
                return 'fair'
        # Slight overprice - might be justified by brand/quality
        elif overpricing_pct <= 20:
            return 'slightly_overpriced'
        # Overpriced but not extreme
        elif overpricing_pct <= 40:
            return 'overpriced'
        # Very expensive
        else:
            return 'highly_overpriced'
