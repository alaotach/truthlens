"""
Advanced browser-based scraper using Playwright
Handles JavaScript-heavy sites and bot detection
"""
import re
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from app.models.schemas import ProductData


class BrowserScraper:
    """Browser automation for scraping product data"""
    
    def __init__(self):
        self.timeout = 15000  # 15 seconds
        
    async def extract_from_url(self, url: str) -> ProductData:
        """
        Extract product data using real browser
        Works with JavaScript sites and bypasses basic bot detection
        """
        try:
            async with async_playwright() as p:
                # Launch browser in headless mode
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                # Add extra headers to avoid detection
                await context.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                })
                
                page = await context.new_page()
                
                # Navigate to URL with longer timeout
                try:
                    await page.goto(url, wait_until='networkidle', timeout=20000)
                except:
                    # Fallback to domcontentloaded if networkidle fails
                    await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
                
                # Wait for content to load
                await page.wait_for_timeout(2000)  # Give time for JS to render
                
                # Get page content
                content = await page.content()
                
                await browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract data
                title = self._extract_title(soup)
                description = self._extract_description(soup)
                price = self._extract_price(soup)
                specs = self._extract_specs(soup)
                currency = self._detect_currency(soup.get_text(), price)
                raw_text = self._get_clean_text(soup)
                
                full_text = f"{title}. {description}. {raw_text}"
                
                # Validate we got meaningful data
                if title == "Unknown Product" and not price:
                    raise ValueError(
                        "Could not extract product information from this page. "
                        "The page structure may not be supported or it requires login."
                    )
                
                return ProductData(
                    title=title,
                    description=description or "No description available",
                    price=price,
                    currency=currency,
                    specs=specs,
                    raw_text=full_text[:5000]
                )
                
        except PlaywrightTimeout:
            raise ValueError(
                "⏱️ Page load timeout - The website took too long to respond. "
                "Please copy the product details and use text input mode."
            )
        except Exception as e:
            raise ValueError(
                f"❌ Failed to load page: {str(e)[:100]}. "
                "Please switch to text input and paste product details."
            )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title"""
        selectors = [
            'h1[id*="title"]',
            'h1[id*="productTitle"]',
            'h1.product-title',
            'h1[class*="product"]',
            'h1[data-testid*="title"]',
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
                if len(text) > 10:
                    return text
        
        # Try meta tags
        meta = soup.find('meta', property='og:title')
        if meta and meta.get('content'):
            return meta['content'].strip()
        
        return "Unknown Product"
    
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
            '#product-description',
            '[id*="about"]',
            '[class*="about"]'
        ]
        
        descriptions = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements[:3]:
                text = element.get_text(strip=True)
                if 20 < len(text) < 2000:
                    descriptions.append(text)
        
        if descriptions:
            return ' '.join(descriptions)[:1500]
        
        # Fallback to meta description
        meta = soup.find('meta', property='og:description') or soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
        
        return ""
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price"""
        selectors = [
            '[class*="price"]',
            '[id*="price"]',
            '[data-testid*="price"]',
            '.price-current',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '.a-price .a-offscreen',
            'span.price',
            '[class*="Price"]',
            '[id*="mrp"]',
            '[class*="mrp"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text(strip=True)
                price = self._extract_price_from_text(price_text)
                if price and price > 0:
                    return price
        
        # Try page text
        return self._extract_price_from_text(soup.get_text())
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract numeric price"""
        patterns = [
            r'₹\s*([0-9,]+\.?[0-9]*)',
            r'Rs\.?\s*([0-9,]+\.?[0-9]*)',
            r'INR\s*([0-9,]+\.?[0-9]*)',
            r'MRP[:\s]*₹?\s*([0-9,]+\.?[0-9]*)',
            r'Price[:\s]*₹?\s*([0-9,]+\.?[0-9]*)',
            r'\$\s*([0-9,]+\.?[0-9]*)',
            r'(?:Price|price|Cost:|MRP|mrp)[:\s]*[₹\$€£¥Rs.]?\s*([0-9,]+\.?[0-9]*)',
            r'\b([0-9]{2,6})\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '').replace('\xa0', '')
                try:
                    price = float(price_str)
                    if 1 <= price <= 10000000:
                        return price
                except ValueError:
                    continue
        return None
    
    def _extract_specs(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract technical specifications"""
        specs = {}
        
        # Look for spec tables/lists
        spec_containers = soup.find_all(['table', 'ul', 'div'], class_=re.compile(r'spec|feature|detail', re.I))
        
        for container in spec_containers[:5]:
            text = container.get_text()
            # Extract from text patterns
            patterns = {
                'battery': r'(\d+)\s*mAh',
                'power': r'(\d+\.?\d*)\s*[Ww]att?s?',
                'voltage': r'(\d+\.?\d*)\s*[Vv]olt?s?',
                'weight': r'(\d+\.?\d*)\s*(?:kg|g|grams?)',
            }
            
            for spec_name, pattern in patterns.items():
                if spec_name not in specs:
                    match = re.search(pattern, text, re.I)
                    if match:
                        specs[spec_name] = match.group(0)
        
        return specs
    
    def _detect_currency(self, text: str, price: Optional[float]) -> str:
        """Detect currency"""
        if not price:
            return "USD"
        
        text_lower = text.lower()
        
        if '₹' in text or 'inr' in text_lower or 'rupee' in text_lower or 'rs.' in text or 'rs ' in text:
            return "INR"
        elif '€' in text or 'eur' in text_lower:
            return "EUR"
        elif '£' in text or 'gbp' in text_lower:
            return "GBP"
        elif '$' in text or 'usd' in text_lower:
            return "USD"
        
        # Heuristic: Indian prices are typically higher
        if price > 500:
            return "INR"
        return "USD"
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text"""
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:3000]


def extract_from_url_sync(url: str) -> ProductData:
    """Synchronous wrapper for async scraper"""
    scraper = BrowserScraper()
    return asyncio.run(scraper.extract_from_url(url))
