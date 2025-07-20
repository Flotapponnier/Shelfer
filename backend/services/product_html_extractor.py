"""
Advanced Product HTML Context Extractor

This service extracts the most relevant HTML sections for product analysis using multiple strategies:
1. Semantic section detection based on e-commerce patterns
2. Content density and relevance analysis  
3. Schema.org integration for guided extraction
4. DOM hierarchy analysis for main product containers
5. Multi-section intelligent aggregation

The goal is to provide clean, focused HTML that contains only the main product information,
removing navigation, ads, suggestions, and other irrelevant content.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class ProductHtmlExtractor:
    """Advanced extractor for product-relevant HTML content."""
    
    def __init__(self):
        # Primary product container selectors (highest priority)
        self.primary_selectors = [
            '[itemtype*="schema.org/Product"]',
            '.product-details',
            '.product-info', 
            '.product-main',
            '.product-content',
            '#product-details',
            '#product-info',
            '.pdp-content',
            '.item-details'
        ]
        
        # Secondary product section selectors
        self.secondary_selectors = [
            '.product-description',
            '.product-specifications',
            '.product-features',
            '.product-overview',
            '.product-summary',
            '.product-title',
            '.product-price',
            '.product-availability',
            '.product-brand',
            '.product-category',
            '.product-reviews',
            '.product-rating',
            '.product-offers'
        ]
        
        # Semantic product indicators (class/id patterns)
        self.product_patterns = [
            r'product[-_]?(?:detail|info|content|main|page|view|section)',
            r'item[-_]?(?:detail|info|content|main|page|view)',
            r'pdp(?:[-_]content|[-_]main)?',
            r'(?:main[-_])?product(?:[-_]wrapper)?',
            r'content[-_]?(?:product|item)',
            r'detail[-_]?(?:product|item|page)'
        ]
        
        # Content type indicators for relevance scoring (expanded)
        self.content_indicators = {
            'title': ['h1', 'h2', 'h3', '.title', '.name', '.product-name', '.item-name', '.product-title'],
            'description': ['.description', '.summary', '.overview', '.details', '.content', '.text', '.info', 
                          '.product-description', '.product-content', '.product-text', '.rte', '.wysiwyg'],
            'price': ['.price', '.cost', '.amount', '.currency', '.offer', '.money'],
            'brand': ['.brand', '.manufacturer', '.maker', '.vendor'],
            'features': ['.features', '.specifications', '.specs', '.attributes', '.properties', '.tech-specs'],
            'reviews': ['.review', '.rating', '.feedback', '.testimonial', '.comments'],
            'availability': ['.stock', '.availability', '.in-stock', '.out-of-stock', '.delivery'],
            'specifications': ['dl', 'dt', 'dd', '.spec-list', '.product-specs', '.tech-details'],
            'tabs': ['.tab-content', '.tab-pane', '.accordion-content', '.collapsible-content']
        }
        
        # Elements to always remove (noise) - reduced list, more selective
        self.noise_selectors = [
            'nav', 'header', 'footer', 
            '.navigation', '.nav', '.menu',
            '.advertisement', '.ad', '.ads',
            '.sidebar', '.recommendations', '.suggested',
            '.social', '.share', '.newsletter',
            '.breadcrumb', '.breadcrumbs',
            '.search', '.search-form',
            'script', 'style', 'noscript',
            '.cookie', '.popup', '.modal',
            '.chat', '.support', '.help',
            # Payment and checkout widgets (keep these aggressive)
            '.shopify-payment-button', 'shopify-accelerated-checkout',
            'shopify-paypal-button', '.paypal-buttons',
            '.payment-button', '.checkout-button',
            # Image gallery navigation (keep these aggressive)
            '.flickity-page-dots', '.carousel-dots', '.image-dots',
            '.carousel-nav', '.slider-nav', '.gallery-nav',
            # Remove related products but keep main product content
            '.related-products', '.also-bought', '.cross-sell'
        ]
        
        # Attributes to clean from elements
        self.clean_attributes = [
            'onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout',
            'style', 'class', 'id',  # Optional: keep for debugging, remove for production
            'data-analytics', 'data-tracking', 'data-gtm',
            'data-testid', 'data-test'
        ]

    async def extract_product_html_context(self, page, product_name: str = None, schema_data: Dict = None) -> str:
        """
        Extract the most relevant HTML context for product analysis.
        
        Args:
            page: Playwright page object
            product_name: Product name for relevance scoring
            schema_data: Existing schema.org data for guided extraction
            
        Returns:
            Clean, relevant HTML context for the main product
        """
        try:
            # Strategy 1: Find main product containers using semantic selectors
            product_containers = await self._find_product_containers(page)
            
            # Strategy 2: Analyze content relevance and density
            content_sections = await self._analyze_content_sections(page, product_name)
            
            # Strategy 3: Use schema.org data to guide extraction (if available)
            schema_guided_sections = await self._extract_schema_guided_sections(page, schema_data) if schema_data else []
            
            # Strategy 4: Find main content area via DOM hierarchy
            main_content_area = await self._find_main_content_area(page)
            
            # Combine and score all discovered sections
            all_sections = self._combine_and_score_sections(
                product_containers, content_sections, schema_guided_sections, main_content_area, product_name
            )
            
            # Select the best sections and merge them
            selected_html = await self._select_and_merge_sections(page, all_sections)
            
            # Clean and optimize the final HTML
            cleaned_html = self._clean_and_optimize_html(selected_html)
            
            logger.info(f"ProductHtmlExtractor: Extracted {len(cleaned_html)} chars of relevant HTML context")
            return cleaned_html
            
        except Exception as e:
            logger.error(f"Failed to extract product HTML context: {e}")
            return ""

    async def _find_product_containers(self, page) -> List[Dict]:
        """Find primary product containers using semantic selectors."""
        containers = []
        
        # Extract using JavaScript for better performance
        container_data = await page.evaluate(f"""
            () => {{
                const containers = [];
                const primarySelectors = {json.dumps(self.primary_selectors)};
                const productPatterns = {json.dumps(self.product_patterns)};
                
                // Find by semantic selectors
                primarySelectors.forEach(selector => {{
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {{
                        if (el.innerHTML.trim()) {{
                            containers.push({{
                                html: el.outerHTML,
                                selector: selector,
                                type: 'semantic',
                                score: 100,
                                textLength: el.innerText.length,
                                elementCount: el.querySelectorAll('*').length
                            }});
                        }}
                    }});
                }});
                
                // Find by pattern matching on class/id
                productPatterns.forEach(pattern => {{
                    const regex = new RegExp(pattern, 'i');
                    const allElements = document.querySelectorAll('*');
                    allElements.forEach(el => {{
                        const className = el.className || '';
                        const id = el.id || '';
                        if (regex.test(className) || regex.test(id)) {{
                            if (el.innerHTML.trim() && el.innerText.length > 100) {{
                                containers.push({{
                                    html: el.outerHTML,
                                    selector: `pattern:${{pattern}}`,
                                    type: 'pattern',
                                    score: 80,
                                    textLength: el.innerText.length,
                                    elementCount: el.querySelectorAll('*').length
                                }});
                            }}
                        }}
                    }});
                }});
                
                return containers;
            }}
        """)
        
        return container_data

    async def _analyze_content_sections(self, page, product_name: str = None) -> List[Dict]:
        """Analyze content sections for product relevance."""
        sections = []
        
        content_data = await page.evaluate(f"""
            (productName) => {{
                const sections = [];
                const contentIndicators = {json.dumps(self.content_indicators)};
                
                // Analyze each content type
                Object.entries(contentIndicators).forEach(([type, selectors]) => {{
                    selectors.forEach(selector => {{
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {{
                            if (el.innerText.trim().length > 20) {{
                                let relevanceScore = 0;
                                const text = el.innerText.toLowerCase();
                                
                                // Score based on content type
                                if (type === 'title') relevanceScore += 50;
                                else if (type === 'description') relevanceScore += 40;
                                else if (type === 'price') relevanceScore += 35;
                                else relevanceScore += 25;
                                
                                // Boost score if product name appears in text
                                if (productName && typeof productName === 'string' && productName.trim()) {{
                                    const nameWords = productName.toLowerCase().split(' ').filter(word => word.trim());
                                    nameWords.forEach(word => {{
                                        if (word.length > 3 && text.includes(word)) {{
                                            relevanceScore += 15;
                                        }}
                                    }});
                                }}
                                
                                sections.push({{
                                    html: el.outerHTML,
                                    selector: selector,
                                    type: 'content',
                                    contentType: type,
                                    score: relevanceScore,
                                    textLength: el.innerText.length,
                                    elementCount: el.querySelectorAll('*').length
                                }});
                            }}
                        }});
                    }});
                }});
                
                return sections;
            }}
        """, product_name)
        
        return content_data

    async def _extract_schema_guided_sections(self, page, schema_data: Dict) -> List[Dict]:
        """Use schema.org data to find relevant HTML sections."""
        if not schema_data:
            return []
            
        sections = []
        
        # Extract key product properties from schema
        product_properties = {}
        if schema_data.get('@type') == 'Product':
            product_properties = {
                'name': schema_data.get('name'),
                'description': schema_data.get('description'),
                'brand': schema_data.get('brand', {}).get('name') if isinstance(schema_data.get('brand'), dict) else schema_data.get('brand'),
                'price': schema_data.get('offers', {}).get('price') if isinstance(schema_data.get('offers'), dict) else None
            }
        
        # Find HTML elements that contain schema property values
        schema_data_str = await page.evaluate(f"""
            (properties) => {{
                const sections = [];
                
                Object.entries(properties).forEach(([prop, value]) => {{
                    if (value && typeof value === 'string' && value.length > 3) {{
                        // Find elements containing this schema value
                        const allElements = document.querySelectorAll('*');
                        allElements.forEach(el => {{
                            if (el.innerText.includes(value) && el.innerText.length < 1000) {{
                                sections.push({{
                                    html: el.outerHTML,
                                    selector: `schema:${{prop}}`,
                                    type: 'schema-guided',
                                    schemaProperty: prop,
                                    score: 70,
                                    textLength: el.innerText.length,
                                    elementCount: el.querySelectorAll('*').length
                                }});
                            }}
                        }});
                    }}
                }});
                
                return sections;
            }}
        """, product_properties)
        
        return schema_data_str

    async def _find_main_content_area(self, page) -> List[Dict]:
        """Find the main content area using DOM hierarchy analysis."""
        main_areas = await page.evaluate("""
            () => {
                const areas = [];
                
                // Look for semantic main content elements
                const mainSelectors = [
                    'main', '[role="main"]', '#main', '.main',
                    '#content', '.content', '.main-content',
                    '#primary', '.primary', '.primary-content',
                    'article', '[role="article"]'
                ];
                
                mainSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        if (el.innerText.length > 500) {  // Substantial content
                            areas.push({
                                html: el.outerHTML,
                                selector: selector,
                                type: 'main-area',
                                score: 60,
                                textLength: el.innerText.length,
                                elementCount: el.querySelectorAll('*').length
                            });
                        }
                    });
                });
                
                return areas;
            }
        """)
        
        return main_areas

    def _combine_and_score_sections(self, *section_lists, product_name: str = None) -> List[Dict]:
        """Combine all discovered sections and calculate final scores."""
        all_sections = []
        
        # Flatten all section lists
        for section_list in section_lists:
            if section_list:
                all_sections.extend(section_list)
        
        # Deduplicate by similar content (avoid selecting the same element multiple times)
        unique_sections = []
        seen_signatures = set()
        
        for section in all_sections:
            # Create a signature based on first 200 chars of text content
            signature = self._get_section_signature(section.get('html', ''))
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_sections.append(section)
        
        # Apply additional scoring factors
        for section in unique_sections:
            # Size score (prefer substantial but not overwhelming content)
            text_length = section.get('textLength', 0)
            if 100 <= text_length <= 2000:
                section['score'] += 20
            elif 2000 < text_length <= 5000:
                section['score'] += 10
            elif text_length > 10000:
                section['score'] -= 20  # Too large, likely contains noise
            
            # Element complexity score (prefer structured content)
            element_count = section.get('elementCount', 0)
            if 5 <= element_count <= 50:
                section['score'] += 15
            elif element_count > 100:
                section['score'] -= 10  # Too complex, likely contains navigation/ads
        
        # Sort by score (highest first)
        unique_sections.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return unique_sections

    async def _select_and_merge_sections(self, page, sections: List[Dict]) -> str:
        """Select the best sections and merge them intelligently."""
        if not sections:
            return ""
        
        selected_sections = []
        # Remove length limit for debugging - take all good sections
        max_sections = 5  # Limit by number of sections instead
        
        # Select top sections
        for i, section in enumerate(sections):
            if i < max_sections:
                selected_sections.append(section)
            else:
                break
        
        # If we only have one good section, use it
        if len(selected_sections) == 1:
            return selected_sections[0].get('html', '')
        
        # For multiple sections, merge them in a container
        if len(selected_sections) > 1:
            merged_html = '<div class="merged-product-context">\n'
            for i, section in enumerate(selected_sections):
                merged_html += f'  <div class="product-section-{i}" data-source="{section.get("selector", "unknown")}">\n'
                merged_html += f'    {section.get("html", "")}\n'
                merged_html += f'  </div>\n'
            merged_html += '</div>'
            return merged_html
        
        return ""

    def _clean_and_optimize_html(self, html: str) -> str:
        """Clean and optimize the HTML for analysis."""
        if not html:
            return ""
        
        # Remove script and style content first (most aggressive)
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove payment widgets (Shopify/PayPal specific)
        html = re.sub(r'<shopify-[^>]*>.*?</shopify-[^>]*>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<iframe[^>]*paypal[^>]*>.*?</iframe>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<iframe[^>]*payment[^>]*>.*?</iframe>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove elements with huge data attributes (tracking/widget configs)
        html = re.sub(r'<[^>]*data-[^=]*="[^"]{500,}"[^>]*>.*?</[^>]*>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove SVG icons and complex graphics
        html = re.sub(r'<svg[^>]*>.*?</svg>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove noise elements by class/id patterns (more selective)
        noise_patterns = [
            # Payment related (keep these aggressive)
            r'<[^>]*class="[^"]*payment[^"]*"[^>]*>.*?</[^>]*>',
            r'<[^>]*class="[^"]*paypal[^"]*"[^>]*>.*?</[^>]*>',
            r'<[^>]*class="[^"]*checkout[^"]*"[^>]*>.*?</[^>]*>',
            # Social sharing (keep these aggressive) 
            r'<[^>]*class="[^"]*share[^"]*"[^>]*>.*?</[^>]*>',
            r'<[^>]*class="[^"]*social[^"]*"[^>]*>.*?</[^>]*>',
            # Navigation dots/buttons (keep these aggressive)
            r'<[^>]*class="[^"]*dot[^"]*"[^>]*>.*?</[^>]*>',
            r'<[^>]*class="[^"]*flickity[^"]*"[^>]*>.*?</[^>]*>',
            r'<[^>]*class="[^"]*carousel[^"]*"[^>]*>.*?</[^>]*>',
            # Only remove specific action buttons (more selective)
            r'<button[^>]*aria-label="(Zoom|Share|Close)"[^>]*>.*?</button>',
            r'<[^>]*class="[^"]*roundbutton[^"]*"[^>]*>.*?</[^>]*>',
        ]
        
        for pattern in noise_patterns:
            html = re.sub(pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove noise elements by selector
        for selector in self.noise_selectors:
            if selector.startswith('.'):
                class_name = selector[1:]
                html = re.sub(rf'<[^>]*class="[^"]*{re.escape(class_name)}[^"]*"[^>]*>.*?</[^>]*>', '', html, flags=re.DOTALL | re.IGNORECASE)
            elif selector.startswith('#'):
                id_name = selector[1:]
                html = re.sub(rf'<[^>]*id="[^"]*{re.escape(id_name)}[^"]*"[^>]*>.*?</[^>]*>', '', html, flags=re.DOTALL | re.IGNORECASE)
            else:
                # Tag removal
                html = re.sub(rf'<{re.escape(selector)}[^>]*>.*?</{re.escape(selector)}>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up only the most problematic attributes (less aggressive)
        attribute_patterns = [
            r'data-[^=]*="[^"]{100,}"',  # Only remove very long data attributes (tracking)
            r'aria-describedby="[^"]*"', # Remove specific aria attributes that add noise
            r'aria-labelledby="[^"]*"',
            r'style="[^"]*"',            # Remove inline styles
        ]
        
        for pattern in attribute_patterns:
            html = re.sub(pattern, '', html, flags=re.IGNORECASE)
        
        # Clean up whitespace and empty elements (less aggressive)
        html = re.sub(r'\s+', ' ', html)
        html = re.sub(r'>\s+<', '><', html)
        # Only remove truly empty elements, not those with just whitespace that might contain text nodes
        html = re.sub(r'<([^>]+)></\1>', '', html)  # Remove completely empty elements only
        
        # Remove size limit for debugging - show full content
        # if len(html) > 8000:
        #     html = html[:8000] + "..."
        
        return html.strip()

    def _get_section_signature(self, html: str) -> str:
        """Generate a signature for deduplication."""
        if not html:
            return ""
        
        # Extract text content
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Return first 200 chars as signature
        return text[:200]