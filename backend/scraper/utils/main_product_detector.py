"""
Main Product Detection Algorithm

This module implements intelligent algorithms to identify the primary/main product
on e-commerce pages, filtering out suggestions, recommendations, and related products.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
import logging

# Set up logger
logger = logging.getLogger(__name__)


class MainProductDetector:
    """
    Detects the main product on an e-commerce page by analyzing:
    1. URL patterns and structure
    2. HTML element positioning and hierarchy
    3. Product schema completeness and quality
    4. Page layout patterns
    """
    
    def __init__(self, config=None):
        """
        Initialize main product detector.
        
        Args:
            config: Optional DetectionConfig instance, uses global config if None
        """
        if config is None:
            # Use default config
            self.config = self._get_default_config()
        else:
            self.config = config.config if hasattr(config, 'config') else config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'main_product_url_patterns': [
                r'/products?/([^/]+)/?$',
                r'/liquids/([^/]+)/?$',
                r'/item/([^/]+)/?$',
                r'/p/([^/]+)/?$',
                r'/buy/([^/]+)/?$',
                r'/detail/([^/]+)/?$',
                r'/shop/([^/]+)/?$',
                r'/([^/]+)\.html?$',
                r'/([^/]+)\.html?[#?]',
            ],
            'suggestion_indicators': [
                'related', 'recommended', 'suggestion', 'similar', 'other',
                'you-might', 'also-like', 'customers-also', 'more-from',
                'recently-viewed', 'trending', 'popular', 'bestseller',
                'bundle', 'addon', 'accessory', 'complement'
            ],
            'main_product_indicators': [
                'product-main', 'product-detail', 'product-info', 'product-page',
                'main-product', 'primary-product', 'product-hero', 'product-focus',
                'pdp-main', 'item-detail', 'product-container', 'product-wrapper'
            ],
            'scoring_thresholds': {
                'url_match_strong': 70,
                'score_difference_clear': 15,
                'high_confidence_minimum': 40
            },
            'scoring_weights': {
                'url_pattern_match': 25,
                'word_match_per_word': 20,
                'high_ratio_bonus': 30,
                'exact_substring_match': 50,
                'schema_essential_field': 5,
                'schema_detailed_field': 2,
                'offer_price': 8,
                'html_main_indicator': 15,
                'html_position_above_fold': 10
            }
        }

    async def identify_main_product(self, page, products: List[Dict[str, Any]], 
                                  current_url: str) -> Optional[Dict[str, Any]]:
        """
        Identify the main product from a list of products found on the page.
        
        Args:
            page: Playwright page object for HTML analysis
            products: List of product schemas found on the page
            current_url: The URL being analyzed
            
        Returns:
            The main product schema or None if no clear main product is found
        """
        if not products:
            logger.warning("No products provided for main product detection")
            return None
            
        if len(products) == 1:
            logger.info("Single product found - assuming it's the main product")
            return products[0]
        
        logger.info(f"Multiple products found ({len(products)}), analyzing to find main product...")
        
        # First, try URL-based matching (most reliable)
        url_matched_product = self._find_product_by_url_match(products, current_url)
        if url_matched_product:
            logger.info(f"Found product by URL matching: {url_matched_product.get('name', 'Unnamed')}")
            return url_matched_product
        
        # Fallback to comprehensive scoring
        product_scores = []
        for i, product in enumerate(products):
            try:
                score = await self._calculate_product_score(page, product, current_url)
                product_scores.append((product, score))
                product_name = product.get('name', 'Unnamed Product')[:50]
                logger.info(f"Product {i+1}: '{product_name}' - Score: {score}")
            except Exception as e:
                logger.error(f"Error scoring product {i+1}: {e}")
                # Add with minimal score to keep it in consideration
                product_scores.append((product, 0))
            
        # Sort by score (highest first)
        product_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the highest scoring product
        best_product, best_score = product_scores[0]
        
        # Enhanced decision logic using config thresholds
        thresholds = self.config['scoring_thresholds']
        
        if len(product_scores) > 1:
            second_best_score = product_scores[1][1]
            score_difference = best_score - second_best_score
            
            if score_difference >= thresholds['score_difference_clear']:
                logger.info(f"Clear main product identified with score {best_score} (margin: {score_difference})")
                return best_product
            elif best_score >= thresholds['high_confidence_minimum']:
                logger.info(f"High confidence main product with score {best_score}")
                return best_product
            else:
                logger.warning(f"Ambiguous main product detection - best: {best_score}, second: {second_best_score}")
        
        # Always return the best product (even with low confidence)
        logger.info(f"Returning best scoring product with score {best_score}")
        return best_product

    def _find_product_by_url_match(self, products: List[Dict[str, Any]], current_url: str) -> Optional[Dict[str, Any]]:
        """Find the product that best matches the current URL."""
        logger.info(f"Attempting URL-based product matching for: {current_url}")
        
        # Extract the URL slug (filename without extension and parameters)
        from urllib.parse import urlparse
        parsed_url = urlparse(current_url)
        url_path = parsed_url.path
        
        # Get the filename part
        url_slug = url_path.split('/')[-1]
        if '.' in url_slug:
            url_slug = url_slug.split('.')[0]  # Remove extension
        
        logger.info(f"URL slug extracted: '{url_slug}'")
        
        best_match = None
        best_score = 0
        
        for product in products:
            product_name = product.get('name', '')
            if not product_name:
                continue
                
            # Calculate URL relevance score
            score = self._calculate_url_relevance(product_name, url_slug, current_url)
            
            logger.info(f"Product '{product_name[:30]}...' URL relevance score: {score}")
            
            if score > best_score:
                best_score = score
                best_match = product
        
        # Only return if we have a strong match
        threshold = self.config['scoring_thresholds']['url_match_strong']
        if best_score > threshold:
            logger.info(f"Strong URL match found with score {best_score}")
            return best_match
        
        logger.info(f"No strong URL match found (best score: {best_score})")
        return None
    
    def _calculate_url_relevance(self, product_name: str, url_slug: str, full_url: str) -> int:
        """Calculate how well a product name matches the URL."""
        if not product_name or not url_slug:
            return 0
        
        score = 0
        
        # Clean product name and URL for comparison
        clean_product_name = re.sub(r'[^a-zA-Z0-9]', '', product_name.lower())
        clean_url_slug = re.sub(r'[^a-zA-Z0-9]', '', url_slug.lower())
        clean_full_url = re.sub(r'[^a-zA-Z0-9]', '', full_url.lower())
        
        # Extract significant words from product name (> 3 chars)
        product_words = [word.lower() for word in re.findall(r'\w+', product_name) if len(word) > 3]
        
        # Check each significant word in URL
        weights = self.config['scoring_weights']
        words_in_url = 0
        for word in product_words:
            if word in clean_url_slug or word in clean_full_url:
                words_in_url += 1
                score += weights['word_match_per_word']
        
        # Bonus for high word match ratio
        if product_words:
            match_ratio = words_in_url / len(product_words)
            if match_ratio >= 0.8:  # 80% or more words match
                score += 30
            elif match_ratio >= 0.6:  # 60% or more words match
                score += 20
            elif match_ratio >= 0.4:  # 40% or more words match
                score += 10
        
        # Check for exact substring matches
        if clean_product_name in clean_url_slug:
            score += 50  # Strong bonus for exact match
        elif clean_product_name in clean_full_url:
            score += 30  # Medium bonus for match in full URL
        
        # Penalty for very short names (likely generic)
        if len(product_name) < 10:
            score -= 10
        
        logger.debug(f"URL relevance calculation: '{product_name}' vs '{url_slug}' = {score} points")
        return score

    async def _calculate_product_score(self, page, product: Dict[str, Any], 
                                     current_url: str) -> int:
        """Calculate a comprehensive score for a product to determine if it's the main product."""
        score = 0
        product_name = product.get('name', '')
        
        # 1. URL Pattern Analysis (40 points max)
        url_score = self._analyze_url_patterns(current_url, product_name)
        score += url_score
        logger.debug(f"URL pattern score: {url_score}")
        
        # 2. Schema Completeness (30 points max)
        schema_score = self._analyze_schema_completeness(product)
        score += schema_score
        logger.debug(f"Schema completeness score: {schema_score}")
        
        # 3. HTML Context Analysis (40 points max)
        try:
            html_score = await self._analyze_html_context(page, product)
            score += html_score
            logger.debug(f"HTML context score: {html_score}")
        except Exception as e:
            logger.warning(f"Failed to analyze HTML context: {e}")
            html_score = 0
        
        # 4. Product Name Quality (20 points max)
        name_score = self._analyze_product_name(product_name, current_url)
        score += name_score
        logger.debug(f"Product name score: {name_score}")
        
        # 5. Offer Quality (20 points max)
        offer_score = self._analyze_offer_quality(product)
        score += offer_score
        logger.debug(f"Offer quality score: {offer_score}")
        
        return score

    def _analyze_url_patterns(self, url: str, product_name: str) -> int:
        """Analyze URL patterns to determine if this is likely a main product page."""
        score = 0
        weights = self.config['scoring_weights']
        
        # Check if URL matches main product patterns
        for pattern in self.config['main_product_url_patterns']:
            if re.search(pattern, url, re.IGNORECASE):
                score += weights['url_pattern_match']
                logger.debug(f"URL matches main product pattern: {pattern}")
                break
        
        # Advanced product name matching in URL
        if product_name:
            # Extract key words from product name (longer than 3 chars)
            product_words = [word.lower() for word in re.findall(r'\w+', product_name) if len(word) > 3]
            url_lower = url.lower()
            
            # Count how many product words appear in URL
            matching_words = 0
            for word in product_words:
                if word in url_lower:
                    matching_words += 1
                    logger.debug(f"Product word '{word}' found in URL")
            
            if product_words:  # Avoid division by zero
                match_ratio = matching_words / len(product_words)
                score += int(match_ratio * 30)  # Up to 30 points for full match
                logger.debug(f"Product name URL match: {matching_words}/{len(product_words)} words ({match_ratio:.2%})")
        
        # Check for suggestion indicators in URL (negative score)
        for indicator in self.suggestion_indicators:
            if indicator in url.lower():
                score -= 20
                logger.debug(f"Suggestion indicator found in URL: {indicator}")
                break
        
        return max(0, score)

    def _analyze_schema_completeness(self, product: Dict[str, Any]) -> int:
        """Analyze the completeness and quality of the product schema."""
        score = 0
        
        # Essential fields present
        essential_fields = ['name', 'description', 'offers', 'image']
        for field in essential_fields:
            if product.get(field):
                score += 5
        
        # Detailed fields present
        detailed_fields = ['brand', 'sku', 'mpn', 'gtin13', 'aggregateRating', 'review']
        for field in detailed_fields:
            if product.get(field):
                score += 2
        
        # High-quality offer information
        offers = product.get('offers', {})
        if isinstance(offers, dict):
            if offers.get('price'):
                score += 3
            if offers.get('priceCurrency'):
                score += 2
            if offers.get('availability'):
                score += 2
        
        return min(30, score)

    async def _analyze_html_context(self, page, product: Dict[str, Any]) -> int:
        """Analyze HTML context to determine product positioning on the page."""
        score = 0
        product_name = product.get('name', '')
        
        if not product_name:
            logger.debug("No product name available for HTML context analysis")
            return 10  # Give a small base score instead of 0
        
        try:
            # Escape the product name for safe JavaScript evaluation
            safe_product_name = product_name.replace('"', '\\"').replace("'", "\\'")
            
            # Find elements containing the product name
            name_elements = await page.evaluate(f"""
                () => {{
                    try {{
                        const productName = "{safe_product_name}";
                        const elements = [];
                        
                        // Search in main content areas first
                        const searchAreas = [
                            document.querySelector('#main-product-wrapper'),
                            document.querySelector('.product-container'),
                            document.querySelector('.product-page'),
                            document.querySelector('.product-detail'),
                            document.querySelector('main'),
                            document.body
                        ].filter(area => area);
                        
                        for (const area of searchAreas) {{
                            const walker = document.createTreeWalker(
                                area,
                                NodeFilter.SHOW_TEXT,
                                null,
                                false
                            );
                            
                            let node;
                            while (node = walker.nextNode()) {{
                                if (node.textContent && node.textContent.includes(productName)) {{
                                    const element = node.parentElement;
                                    if (element) {{
                                        const rect = element.getBoundingClientRect();
                                        elements.push({{
                                            tagName: element.tagName,
                                            className: element.className || '',
                                            id: element.id || '',
                                            offsetTop: rect.top + window.scrollY,
                                            offsetLeft: rect.left + window.scrollX,
                                            offsetWidth: rect.width,
                                            offsetHeight: rect.height
                                        }});
                                    }}
                                }}
                            }}
                        }}
                        return elements;
                    }} catch (error) {{
                        console.log('HTML context analysis error:', error);
                        return [];
                    }}
                }}
            """)
            
            if name_elements:
                # Analyze positioning and context
                for element in name_elements:
                    # Check for main product indicators in classes/IDs
                    classes_and_id = f"{element.get('className', '')} {element.get('id', '')}".lower()
                    
                    for indicator in self.main_product_indicators:
                        if indicator in classes_and_id:
                            score += 15
                            logger.debug(f"Main product indicator found: {indicator}")
                    
                    # Check for suggestion indicators (negative)
                    for indicator in self.suggestion_indicators:
                        if indicator in classes_and_id:
                            score -= 10
                            logger.debug(f"Suggestion indicator found: {indicator}")
                    
                    # Positioning analysis (main products are usually higher on page)
                    offset_top = element.get('offsetTop', 0)
                    if offset_top < 500:  # Above the fold
                        score += 10
                    elif offset_top < 1000:  # Still relatively high
                        score += 5
                    
                    # Size analysis (main products usually have larger elements)
                    width = element.get('offsetWidth', 0)
                    height = element.get('offsetHeight', 0)
                    area = width * height
                    
                    if area > 100000:  # Large element
                        score += 8
                    elif area > 50000:  # Medium element
                        score += 5
        
        except Exception as e:
            logger.warning(f"HTML context analysis failed: {e}")
            return 0
        
        return min(40, max(0, score))

    def _analyze_product_name(self, product_name: str, url: str) -> int:
        """Analyze product name quality and URL alignment."""
        if not product_name:
            return 0
        
        score = 0
        
        # Name length (longer names are often more specific/main products)
        name_length = len(product_name.strip())
        if name_length > 50:
            score += 8
        elif name_length > 20:
            score += 5
        elif name_length > 10:
            score += 3
        
        # Check for generic/suggestion terms in name
        for indicator in self.suggestion_indicators:
            if indicator in product_name.lower():
                score -= 5
        
        # URL-name alignment
        parsed_url = urlparse(url)
        url_path = parsed_url.path.lower()
        name_words = re.findall(r'\w+', product_name.lower())
        
        # Count how many name words appear in URL
        url_word_matches = sum(1 for word in name_words if len(word) > 3 and word in url_path)
        if name_words:
            alignment_ratio = url_word_matches / len(name_words)
            score += int(alignment_ratio * 12)
        
        return min(20, max(0, score))

    def _analyze_offer_quality(self, product: Dict[str, Any]) -> int:
        """Analyze the quality and completeness of offer information."""
        score = 0
        offers = product.get('offers', {})
        
        if not offers:
            return 0
        
        # Handle both single offer and array of offers
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        # Price information
        if offers.get('price'):
            score += 8
        if offers.get('priceCurrency'):
            score += 4
        
        # Availability information
        availability = offers.get('availability', '')
        if availability:
            score += 4
            # In-stock products are more likely to be main products
            if 'instock' in availability.lower() or 'available' in availability.lower():
                score += 2
        
        # Seller information
        if offers.get('seller'):
            score += 2
        
        return min(20, score)

    def get_main_product_summary(self, main_product: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the detected main product."""
        if not main_product:
            return {}
        
        return {
            'name': main_product.get('name', 'Unknown Product'),
            'sku': main_product.get('sku'),
            'brand': main_product.get('brand', {}).get('name') if isinstance(main_product.get('brand'), dict) else main_product.get('brand'),
            'price': self._extract_price_info(main_product.get('offers', {})),
            'availability': self._extract_availability(main_product.get('offers', {})),
            'image': main_product.get('image'),
            'description': main_product.get('description', '')[:200] + '...' if main_product.get('description', '') else None,
            'rating': self._extract_rating_info(main_product.get('aggregateRating', {})),
            'full_schema': main_product
        }
    
    def _extract_price_info(self, offers) -> Optional[str]:
        """Extract formatted price information from offers."""
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        price = offers.get('price')
        currency = offers.get('priceCurrency', '')
        
        if price:
            return f"{price} {currency}".strip()
        return None
    
    def _extract_availability(self, offers) -> Optional[str]:
        """Extract availability status from offers."""
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        availability = offers.get('availability', '')
        if availability:
            # Clean up schema.org URLs
            if 'schema.org' in availability:
                return availability.split('/')[-1].replace('_', ' ').title()
            return availability
        return None
    
    def _extract_rating_info(self, rating) -> Optional[Dict[str, Any]]:
        """Extract rating information."""
        if not rating:
            return None
        
        return {
            'value': rating.get('ratingValue'),
            'count': rating.get('reviewCount'),
            'best': rating.get('bestRating'),
            'worst': rating.get('worstRating')
        }