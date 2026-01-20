"""
Product data scraper and parser
Extracts product information from URLs or raw text
"""
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import requests
from app.models.schemas import ProductData


class ProductScraper:
    """Handles product data extraction from various sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.timeout = 15
    
    def extract_from_url(self, url: str) -> ProductData:
        """
        Extract product data from URL
        Uses browser automation for better success rate
        """
        # For demo URLs, return example data
        if 'example.com' in url or 'demo' in url.lower():
            return self._create_demo_product(url)
        
        # Try browser-based scraping for real URLs
        try:
            from app.core.browser_scraper import extract_from_url_sync
            result = extract_from_url_sync(url)
            return result
        except ValueError as e:
            # Re-raise ValueError (user-friendly errors)
            raise
        except ImportError:
            # Playwright not installed, use fallback
            return self._extract_with_requests(url)
        except Exception as e:
            # Browser scraping failed, try fallback
            try:
                return self._extract_with_requests(url)
            except Exception:
                # Both methods failed
                raise ValueError(
                    f"🌐 Unable to access this product page. "
                    f"The website may have strict bot protection. "
                    f"Please copy the product details (title, price, features) and use text input mode instead."
                )
    
    def _extract_with_requests(self, url: str) -> ProductData:
        """
        Extract product data from URL
        Supports Amazon, Flipkart-like structure
        For demo purposes, also accepts mock/example URLs
        """
        # For demo: allow mock URLs to return example data
        if 'example.com' in url or 'demo' in url.lower():
            return self._create_demo_product(url)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple extraction strategies
            title = self._extract_title(soup) or self._extract_meta_title(soup)
            description = self._extract_description(soup) or self._extract_meta_description(soup)
            price = self._extract_price(soup)
            specs = self._extract_specs(soup)
            
            # Get more text content for claim extraction
            raw_text = self._get_clean_text(soup)
            
            # If we got minimal data, try to extract from meta tags and structured data
            if title == "Unknown Product":
                title = self._extract_from_json_ld(soup) or title
            
            # Combine all text for better claim extraction
            full_text = f"{title}. {description}. {raw_text}"
            
            # Detect currency from text
            currency = self._detect_currency(soup.get_text(), price)
            
            return ProductData(
                title=title,
                description=description or "No description available",
                price=price,
                currency=currency,
                specs=specs,
                raw_text=full_text[:5000]
            )
        except requests.Timeout:
            raise ValueError(
                "⏱️ Request timeout - The website took too long to respond. "
                "This usually happens with sites that have heavy bot protection. "
                "Please try: 1) Copy the product description and paste it directly, or 2) Use the demo URLs to test the system."
            )
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError(
                    "🚫 Access Denied (403) - This website is blocking automated access. "
                    "Please copy the product description from the page and paste it in text mode instead."
                )
            elif e.response.status_code == 503:
                raise ValueError(
                    "⚠️ Service Unavailable (503) - The website's server is currently unavailable or blocking requests. "
                    "Please copy the product details and use text input mode."
                )
            else:
                raise ValueError(
                    f"❌ HTTP Error {e.response.status_code} - Unable to access this URL. "
                    "Please copy the product information and switch to text input mode."
                )
        except requests.RequestException as e:
            error_msg = str(e)[:100]
            raise ValueError(
                f"🌐 Network Error - Unable to fetch the URL ({error_msg}). "
                "The website may be blocking automated requests. Please use text input mode instead."
            )
        except Exception as e:
            raise ValueError(
                f"❌ Error processing URL: {str(e)[:100]}. "
                "Please switch to text input mode and paste the product details directly."
            )
    
    def extract_from_text(self, text: str) -> ProductData:
        """
        Extract product data from plain text description with validation
        """
        # Input validation
        if not text or len(text.strip()) < 10:
            raise ValueError("Product description is too short. Please provide more details (at least 10 characters).")
        
        if len(text) > 10000:
            text = text[:10000]  # Limit text length for performance
        
        # Extract title (first line or first 100 chars)
        lines = text.strip().split('\n')
        title = lines[0][:200] if lines else text[:200]  # Limit title length
        
        if not title.strip():
            title = "Product"
        
        # Extract price if present
        price = self._extract_price_from_text(text)
        
        # Extract specs using patterns
        specs = self._extract_specs_from_text(text)
        
        # Detect currency from text
        currency = self._detect_currency(text, price)
        
        return ProductData(
            title=title.strip(),
            description=text,
            price=price,
            currency=currency,
            specs=specs,
            raw_text=text
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title from HTML"""
        # Try common title patterns
        selectors = [
            'h1[id*="title"]',
            'h1[id*="productTitle"]',
            'h1.product-title',
            'h1[class*="product"]',
            '[data-testid="product-title"]',
            'h1[class*="title"]',
            '.product-name h1',
            '#product-title',
            'h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 10:  # Ensure it's substantial
                    return text
        
        return "Unknown Product"
    
    def _extract_meta_title(self, soup: BeautifulSoup) -> str:
        """Extract title from meta tags"""
        meta_tags = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('title', {})
        ]
        
        for tag_name, attrs in meta_tags:
            tag = soup.find(tag_name, attrs)
            if tag:
                content = tag.get('content') if tag_name == 'meta' else tag.get_text()
                if content and len(content) > 10:
                    return content.strip()
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        selectors = [
            '[id*="description"]',
            '[class*="description"]',
            '[data-testid*="description"]',
            'div.product-details',
            '[id*="feature"]',
            '[class*="feature"]',
            '.product-description',
            '#product-description'
        ]
        
        descriptions = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements[:3]:  # Get up to 3 description elements
                text = element.get_text(strip=True)
                if len(text) > 20:
                    descriptions.append(text)
        
        if descriptions:
            return ' '.join(descriptions)[:1000]
        
        return soup.get_text()[:1000]  # Fallback to first 1000 chars
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract description from meta tags"""
        meta_tags = [
            ('meta', {'property': 'og:description'}),
            ('meta', {'name': 'description'}),
            ('meta', {'name': 'twitter:description'})
        ]
        
        for tag_name, attrs in meta_tags:
            tag = soup.find(tag_name, attrs)
            if tag:
                content = tag.get('content')
                if content and len(content) > 20:
                    return content.strip()
        
        return ""
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from HTML"""
        selectors = [
            '[class*="price"]',
            '[id*="price"]',
            '[data-testid*="price"]',
            '.price-current',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '.a-price .a-offscreen',
            'span.price'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text(strip=True)
                price = self._extract_price_from_text(price_text)
                if price and price > 0:
                    return price
        
        # Try to find price in page text
        page_text = soup.get_text()
        return self._extract_price_from_text(page_text)
    
    def _detect_currency(self, text: str, price: Optional[float]) -> str:
        """Detect currency from text and price"""
        if not price:
            return "USD"
        
        text_lower = text.lower()
        
        # Check for explicit currency indicators
        if '₹' in text or 'inr' in text_lower or 'rupee' in text_lower or 'rs.' in text_lower or 'rs ' in text_lower:
            return "INR"
        elif '€' in text or 'eur' in text_lower or 'euro' in text_lower:
            return "EUR"
        elif '£' in text or 'gbp' in text_lower or 'pound' in text_lower:
            return "GBP"
        elif '$' in text or 'usd' in text_lower or 'dollar' in text_lower:
            return "USD"
        
        # Heuristic: Indian prices are typically higher numbers without decimals
        if price > 500 and '.' not in str(price):
            return "INR"
        elif price < 500:
            return "USD"
        
        return "USD"  # Default
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract numeric price from text"""
        # Match patterns like $99.99, 99.99, ₹999, etc.
        patterns = [
            r'₹\s*([0-9,]+\.?[0-9]*)',  # Indian Rupee first
            r'Rs\.?\s*([0-9,]+\.?[0-9]*)',  # Rs. format
            r'INR\s*([0-9,]+\.?[0-9]*)',  # INR prefix
            r'MRP[:\s]*₹?\s*([0-9,]+\.?[0-9]*)',  # MRP format
            r'Price[:\s]*₹?\s*([0-9,]+\.?[0-9]*)',  # Price: format
            r'\$\s*([0-9,]+\.?[0-9]*)',  # Dollar
            r'[\€£¥]\s*([0-9,]+\.?[0-9]*)',  # Other currencies
            r'([0-9,]+\.?[0-9]*)\s*(?:INR|USD|EUR|GBP|rupees?|dollars?)',
            r'(?:Price|price|Cost:|cost:|MRP|mrp)[:\s]*[₹\$€£¥]?\s*([0-9,]+\.?[0-9]*)',
            r'\b([0-9]{2,6})\b'  # Plain numbers 99-999999
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '').replace('\u00a0', '')  # Remove commas and nbsp
                try:
                    price = float(price_str)
                    # Sanity check: reasonable price range
                    if 1 <= price <= 10000000:  # Extended for INR prices
                        return price
                except ValueError:
                    continue
        
        return None
    
    def _extract_specs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract technical specifications"""
        specs = {}
        
        # Look for spec tables
        spec_tables = soup.find_all(['table', 'ul'], class_=re.compile(r'spec|feature|detail'))
        
        for table in spec_tables:
            rows = table.find_all(['tr', 'li'])
            for row in rows:
                text = row.get_text()
                # Try to parse key-value pairs
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        specs[key] = value
        
        return specs
    
    def _extract_specs_from_text(self, text: str) -> Dict[str, Any]:
        """Extract specs from plain text"""
        specs = {}
        
        # Extract common patterns
        patterns = {
            'battery': r'(\d+)\s*mAh',
            'power': r'(\d+)\s*[Ww]att?s?',
            'voltage': r'(\d+\.?\d*)\s*[Vv]olt?s?',
            'current': r'(\d+\.?\d*)\s*[Aa]mp?s?',
            'speed': r'(\d+)\s*(?:mph|km/h|kmph)',
            'range': r'(\d+)\s*(?:km|miles?|meters?|metre?s?)',
            'capacity': r'(\d+)\s*(?:GB|TB|MB|L|ml|liters?|litres?)',
            'weight': r'(\d+\.?\d*)\s*(?:kg|g|grams?|lbs?|oz|ounce)',
            'charging_time': r'(\d+\.?\d*)\s*(?:hour|hr|minute|min)s?\s*(?:charge|charging)?',
            'output': r'(\d+\.?\d*)\s*[Ww]\s*output',
        }
        
        text_lower = text.lower()
        for spec_name, pattern in patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                specs[spec_name] = match.group(0)
        
        return specs
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML, removing scripts and styles"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # Limit to first 5000 chars
    
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product info from JSON-LD structured data"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Handle single object
                    if data.get('@type') == 'Product':
                        return data.get('name', '')
                elif isinstance(data, list):
                    # Handle array of objects
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            return item.get('name', '')
            except:
                continue
        return None
    
    def _create_demo_product(self, url: str) -> ProductData:
        """Create demo product data for testing"""
        # Demo products based on URL patterns
        demo_products = {
            'realistic': ProductData(
                title="Portable 10000mAh Power Bank",
                description="Compact 10000mAh portable charger with 18W fast charging support. Dual USB ports allow charging two devices simultaneously. Built-in safety features protect against overcharging. Lightweight design at 200g. Fully charges in 4 hours.",
                price=39.99,
                currency="USD",
                specs={'battery': '10000mAh', 'power': '18W', 'weight': '200g'},
                raw_text="Portable 10000mAh Power Bank. 18W fast charging. Dual USB ports. 200g lightweight. Charges in 4 hours. Price: $39.99"
            ),
            'unrealistic': ProductData(
                title="Quantum AI Power Bank 50000mAh",
                description="Revolutionary 50000mAh quantum battery with AI-powered charging. Charges any phone in just 3 minutes! 200W ultra-fast output. 100% efficiency guaranteed. Military-grade durability. Medical-grade safety certified.",
                price=199.99,
                currency="USD",
                specs={'battery': '50000mAh', 'power': '200W'},
                raw_text="Quantum AI Power Bank 50000mAh. Charges in 3 minutes. 200W output. 100% efficiency. Military-grade. Medical-grade. Price: $199.99"
            )
        }
        
        # Choose demo based on URL content
        if 'unrealistic' in url.lower() or 'bad' in url.lower():
            return demo_products['unrealistic']
        else:
            return demo_products['realistic']
