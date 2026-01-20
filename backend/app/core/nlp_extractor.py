"""
NLP-based claim extraction from product descriptions
Uses pattern matching and keyword detection to identify product claims
"""
import re
from typing import List, Dict, Optional, Tuple
from app.models.schemas import Claim, ProductData


class ClaimExtractor:
    """Extracts structured claims from product text"""
    
    def __init__(self):
        # Performance claim patterns with categories
        self.claim_patterns = {
            'battery_capacity': {
                'patterns': [
                    r'(\d+)\s*mAh',
                    r'(\d+)\s*milliamp hour',
                    r'battery.*?(\d+)\s*mAh',
                    r'(\d+)\s*[Ww]h(?:our)?',
                    r'capacity[:\s]+(\d+)\s*mAh',
                    r'(\d+,\d+)\s*mAh',  # Format like 10,000mAh
                    r'battery\s+size[:\s]+(\d+)\s*mAh'
                ],
                'unit': 'mAh',
                'keywords': ['battery', 'capacity', 'power bank', 'cell']
            },
            'charging_time': {
                'patterns': [
                    r'charges?\s+(?:in|within)\s+(\d+)\s*(minutes?|mins?|hours?|hrs?)',
                    r'(\d+)\s*(minutes?|mins?|hours?|hrs?)\s+(?:fast\s+)?(?:charg(?:e|ing)|to\s+full)',
                    r'quick\s+charge.*?(\d+)\s*(minutes?|mins?|hours?|hrs?)',
                    r'full\s+charge.*?(\d+)\s*(hours?|hrs?)',
                    r'charging\s+time[:\s]+(\d+)\s*(hours?|hrs?|minutes?|mins?)',
                    r'(?:0|zero)\s*-?\s*(\d+)\s*%\s+(?:in|within)\s+(\d+)\s*(minutes?|mins?)',
                    r'recharge.*?(?:in|within)\s+(\d+)\s*(hours?|hrs?|minutes?|mins?)',
                    r'(\d+)\s*(min|hr)\s+(?:charge|charging)'
                ],
                'unit': 'time',
                'keywords': ['charge', 'charging time', 'fast charge', 'full charge', 'recharge']
            },
            'power_output': {
                'patterns': [
                    r'(\d+\.?\d*)\s*[Ww](?:att)?(?:\s+(?:output|power|charging|fast))?',
                    r'(\d+\.?\d*)\s*[Ww]\s+(?:fast|quick|rapid|super|hyper)',
                    r'power.*?(\d+\.?\d*)\s*[Ww]',
                    r'output[:\s]+(\d+\.?\d*)\s*[Ww]',
                    r'(\d+\.?\d*)\s*[Ww]\s+(?:Type-?C|USB|PD|QC)'
                ],
                'unit': 'W',
                'keywords': ['power', 'watt', 'output', 'fast charging', 'PD', 'QC']
            },
            'speed': {
                'patterns': [
                    r'(\d+)\s*(?:mph|km/h|kmph|kilometers?\s+per\s+hour)',
                    r'top\s+speed.*?(\d+)',
                    r'speed.*?(\d+)\s*(?:mph|km/h)'
                ],
                'unit': 'speed',
                'keywords': ['speed', 'mph', 'kmph', 'fast']
            },
            'range': {
                'patterns': [
                    r'(?:range|distance).*?(\d+)\s*(?:km|miles?|kilometers?)',
                    r'(\d+)\s*(?:km|miles?)\s+range',
                    r'up\s+to\s+(\d+)\s*(?:km|miles?)'
                ],
                'unit': 'distance',
                'keywords': ['range', 'distance', 'coverage']
            },
            'efficiency': {
                'patterns': [
                    r'(\d+)%\s+efficien(?:cy|t)',
                    r'efficien(?:cy|t).*?(\d+)%',
                    r'(\d+)\s*percent\s+efficient'
                ],
                'unit': '%',
                'keywords': ['efficiency', 'efficient', 'energy saving']
            },
            'weight': {
                'patterns': [
                    r'(\d+\.?\d*)\s*(?:kg|g|grams?|kilograms?|lbs?|pounds?)',
                    r'weighs?.*?(\d+\.?\d*)\s*(?:kg|g|lbs?)',
                    r'(?:ultra|super)?\s*light.*?(\d+\.?\d*)\s*(?:kg|g)'
                ],
                'unit': 'weight',
                'keywords': ['weight', 'lightweight', 'portable']
            },
            'capacity_storage': {
                'patterns': [
                    r'(\d+)\s*(?:GB|TB|MB)',
                    r'storage.*?(\d+)\s*(?:GB|TB)',
                    r'(\d+)\s*(?:liter|litre|L|ml)'
                ],
                'unit': 'capacity',
                'keywords': ['storage', 'capacity', 'memory']
            },
            'voltage': {
                'patterns': [
                    r'(\d+\.?\d*)\s*[Vv](?:olt)?(?:\s+(?:input|output))?',
                    r'voltage[:\s]+(\d+\.?\d*)\s*[Vv]',
                    r'(\d+\.?\d*)\s*[Vv]\s+(?:DC|AC)'
                ],
                'unit': 'V',
                'keywords': ['voltage', 'volt', 'power']
            },
            'current': {
                'patterns': [
                    r'(\d+\.?\d*)\s*[Aa](?:mp)?(?:\s+(?:input|output))?',
                    r'current[:\s]+(\d+\.?\d*)\s*[Aa]',
                    r'(\d+\.?\d*)\s*[Aa]\s+(?:fast|quick)'
                ],
                'unit': 'A',
                'keywords': ['current', 'amp', 'ampere']
            },
            'charge_cycles': {
                'patterns': [
                    r'(\d+)\+?\s*(?:charge\s+)?cycles?',
                    r'(?:up\s+to\s+)?(\d+)\s+(?:charge\s+)?cycles?',
                    r'cycle\s+life[:\s]+(\d+)',
                    r'lifespan[:\s]+(\d+)\s+cycles?'
                ],
                'unit': 'cycles',
                'keywords': ['cycle', 'lifespan', 'durability']
            },
            'warranty': {
                'patterns': [
                    r'(\d+)\s*(?:year|month|yr|mo)\s+warranty',
                    r'warranty[:\s]+(\d+)\s+(?:year|month)',
                    r'(\d+)\s*(?:year|yr)\s+(?:guarantee|coverage)'
                ],
                'unit': 'period',
                'keywords': ['warranty', 'guarantee', 'coverage']
            },
            'temperature': {
                'patterns': [
                    r'(?:operating|working)\s+temp.*?([-\d]+)\s*[°]?[CcFf]',
                    r'([-\d]+)[°]?\s*[Cc]\s+to\s+([-\d]+)[°]?\s*[Cc]',
                    r'temperature.*?([-\d]+)\s*[°]?[CcFf]'
                ],
                'unit': 'temp',
                'keywords': ['temperature', 'operating temp', 'thermal']
            },
            'certifications': {
                'patterns': [
                    r'\b(CE|FCC|RoHS|UL|ETL|CSA)\s+certified',
                    r'\b(ISO\s*\d+)',
                    r'certified\s+(?:by\s+)?(CE|FCC|RoHS|UL)',
                    r'\b(MFi|Made\s+for\s+iPhone)'
                ],
                'unit': 'certification',
                'keywords': ['certified', 'certification', 'approved', 'compliant']
            }
        }
        
        # Marketing buzzwords to flag
        self.buzzwords = [
            'AI-powered', 'AI powered', 'artificial intelligence',
            'medical-grade', 'medical grade', 'hospital grade',
            'military-grade', 'military grade', 'military spec',
            'NASA-approved', 'NASA grade', 'space grade',
            'quantum', 'revolutionary', 'breakthrough', 'patent pending',
            'miracle', 'magic', 'ultimate', 'absolute',
            'guaranteed', '100% safe', 'zero risk', 'risk-free',
            'clinically proven', 'scientifically proven', 'lab tested',
            'professional grade', 'industrial strength',
            'never seen before', 'world first', 'industry leading',
            'unlimited', 'infinite', 'perpetual', 'lifetime',
            'award winning', 'best in class', '#1 rated'
        ]
    
    def extract_claims(self, product_data: ProductData) -> List[Claim]:
        """
        Extract all claims from product data
        Returns list of structured claims
        """
        claims = []
        text = self._prepare_text(product_data)
        
        # Extract performance claims
        for category, config in self.claim_patterns.items():
            category_claims = self._extract_category_claims(
                text, category, config
            )
            claims.extend(category_claims)
        
        # Extract buzzword claims
        buzzword_claims = self._extract_buzzwords(text)
        claims.extend(buzzword_claims)
        
        # Deduplicate claims
        claims = self._deduplicate_claims(claims)
        return claims
    
    def _prepare_text(self, product_data: ProductData) -> str:
        """Combine all product text for analysis"""
        text_parts = [
            product_data.title,
            product_data.description
        ]
        
        # Add specs as text
        for key, value in product_data.specs.items():
            text_parts.append(f"{key}: {value}")
        
        return ' '.join(text_parts)
    
    def _extract_category_claims(
        self, text: str, category: str, config: Dict
    ) -> List[Claim]:
        """Extract claims for a specific category"""
        claims = []
        
        for pattern in config['patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract the full matched text as claim
                claim_text = match.group(0)
                
                # Extract numeric value
                value = None
                try:
                    # Try to get first captured group as value
                    value_str = match.group(1)
                    # Handle comma-separated numbers like "10,000"
                    value_str = value_str.replace(',', '')
                    value = float(re.sub(r'[^\d.]', '', value_str))
                except (IndexError, ValueError):
                    pass
                
                # Get context (surrounding text)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                # Don't add duplicate claims with same context
                if not any(c.text == context.strip() and c.category == category for c in claims):
                    claims.append(Claim(
                        text=context.strip(),
                        category=category,
                        extracted_value=value,
                        unit=config['unit']
                    ))
        
        return claims
    
    def _extract_buzzwords(self, text: str) -> List[Claim]:
        """Extract marketing buzzword claims"""
        claims = []
        
        for buzzword in self.buzzwords:
            pattern = re.compile(r'\b' + re.escape(buzzword) + r'\b', re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                claims.append(Claim(
                    text=context.strip(),
                    category='marketing_buzzword',
                    extracted_value=None,
                    unit=None
                ))
        
        # Deduplicate claims
        claims = self._deduplicate_claims(claims)
        return claims
    
    def _deduplicate_claims(self, claims: List[Claim]) -> List[Claim]:
        """Remove duplicate claims based on category and value"""
        seen = set()
        unique_claims = []
        
        for claim in claims:
            # Create unique key from category and extracted value
            key = (claim.category, claim.extracted_value, claim.unit)
            if key not in seen:
                seen.add(key)
                unique_claims.append(claim)
        
        return unique_claims
    
    def _extract_numeric_claims(self, text: str) -> List[Claim]:
        """Extract comparative claims (2x faster, 50% more, etc.)"""
        claims = []
        
        patterns = [
            r'(\d+)x\s+(?:faster|stronger|better|more\s+powerful)',
            r'(\d+)%\s+(?:faster|stronger|better|more)',
            r'(?:faster|stronger|better)\s+than.*?(?:competition|others|leading)',
            r'(?:best|fastest|strongest|most\s+powerful)\s+(?:in|on)\s+(?:market|earth|world)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                # Try to extract multiplier value
                value = None
                try:
                    value = float(match.group(1))
                except (IndexError, ValueError):
                    pass
                
                claims.append(Claim(
                    text=context.strip(),
                    category='comparative',
                    extracted_value=value,
                    unit='multiplier'
                ))
        
        return claims
