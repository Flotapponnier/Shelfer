"""
Product Image Extraction Utilities

This module extracts all relevant product images from e-commerce pages,
including main product images and additional product gallery images.
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class ProductImageExtractor:
    """Extracts product images from e-commerce pages."""
    
    def __init__(self):
        # CSS selectors for product image containers
        self.image_container_selectors = [
            '.product-images',
            '.product-gallery', 
            '.product-photos',
            '#product-images',
            '.product-image-wrapper',
            '.product-media',
            '.pdp-images',
            '.item-images',
            '.product-slider',
            '.product-carousel'
        ]
        
        # CSS selectors for main product images
        self.main_image_selectors = [
            '.product-image-main img',
            '.product-main-image img',
            '.product-hero img',
            '.main-product-image img',
            '.featured-image img',
            '.primary-image img',
            '[data-main-image] img',
            '.product-cover img'
        ]
        
        # CSS selectors for thumbnail/gallery images
        self.thumbnail_selectors = [
            '.product-thumbnails img',
            '.product-thumbs img', 
            '.image-gallery img',
            '.product-images-thumbs img',
            '.thumbnail img',
            '.gallery-thumb img',
            '[data-thumbnail] img'
        ]
        
        # Image quality indicators (prefer high resolution)
        self.quality_keywords = [
            'large', 'big', 'original', 'full', 'zoom', 'detail',
            'thickbox', 'lightbox', 'popup', 'modal'
        ]
    
    async def extract_product_images(self, page, product_name: str = None) -> Dict[str, Any]:
        """
        Extract all product images from the page.
        
        Args:
            page: Playwright page object
            product_name: Product name for context matching
            
        Returns:
            Dictionary with main image URL and other images
        """
        try:
            # Extract images using JavaScript
            image_data = await page.evaluate("""
                () => {
                    // Helper: pick highest-resolution URL from <picture> srcset
                    function getBestSrcFromPicture(img) {
                        const pic = img.closest('picture');
                        if (!pic) return null;
                        const sources = pic.querySelectorAll('source');
                        for (let i = sources.length - 1; i >= 0; i--) {
                            // Use data-srcset to bypass lazy-loaded low-res srcset
                            const ss = sources[i].getAttribute('data-srcset') || sources[i].getAttribute('srcset');
                            if (ss) {
                                const parts = ss.split(',');
                                let bestUrl = null, bestW = 0;
                                parts.forEach(p => {
                                    const [url, wDesc] = p.trim().split(/\s+/);
                                    const w = parseInt((wDesc||'').replace('w',''), 10);
                                    if (!isNaN(w) && w > bestW) { bestW = w; bestUrl = url; }
                                });
                                if (bestUrl) return bestUrl;
                            }
                        }
                        return null;
                    }
                    const images = {
                        mainImages: [],
                        thumbnails: [],
                        allProductImages: [],
                        imageContainers: []
                    };
                    // Fallback: collect any <img> with data-image-* or data-original-src attributes
                    const dataImgSelectors = [
                        'img[data-image-medium-src]',
                        'img[data-image-large-src]',
                        'img[data-image-thickbox-src]',
                        'img[data-original-src]'
                    ].join(', ');
                    document.querySelectorAll(dataImgSelectors).forEach(img => {
                        try {
                            images.allProductImages.push(getImageInfo(img));
                        } catch (e) { /* ignore */ }
                    });
                    
                    // Main image selectors
                    const mainSelectors = [
                        '.product-image-main img',
                        '.product-main-image img', 
                        '.product-hero img',
                        '.main-product-image img',
                        '.featured-image img',
                        '.primary-image img',
                        '[data-main-image] img',
                        '.product-cover img',
                        '.product-lmage-large img',  // For the Tante Dampf case
                        '.easyzoom img',
                        '.product-image-large img',
                        '.zoom img',
                        '.main-image img'
                    ];
                    
                    // Thumbnail selectors
                    const thumbSelectors = [
                        '.product-thumbnails img',
                        '.product-thumbs img',
                        '.image-gallery img', 
                        '.product-images-thumbs img',
                        '.thumbnail img',
                        '.gallery-thumb img',
                        '[data-thumbnail] img',
                        '.thumb img',
                        '.product-images-small img',
                        '.product-gallery-thumbs img',
                        '.gallery img'
                    ];
                    
                    // Container selectors
                    const containerSelectors = [
                        '.product-images',
                        '.product-gallery',
                        '.product-photos', 
                        '#product-images',
                        '.product-image-wrapper',
                        '.product-media',
                        '.images-container',
                        '#main-product-wrapper .product-cover',
                        '.product-image-container',
                        '.product-slider',
                        '.product-carousel',
                        '.image-gallery-container',
                        '.gallery-container',
                        '.product-view-images',
                        '.product-images-wrapper'
                    ];
                    
                    // Function to extract image info
                    function getImageInfo(img) {
                        const rect = img.getBoundingClientRect();
                        // Try picture srcset first
                        const best = getBestSrcFromPicture(img);
                        const srcUrl = best || img.src || img.getAttribute('data-src') || img.getAttribute('data-image-large-src');
                        return {
                            src: srcUrl,
                            alt: img.alt || '',
                            width: img.naturalWidth || rect.width,
                            height: img.naturalHeight || rect.height,
                            className: img.className || '',
                            dataSrc: img.getAttribute('data-src'),
                            dataLargeSrc: img.getAttribute('data-image-large-src'),
                            dataMediumSrc: img.getAttribute('data-image-medium-src'),
                            dataZoomSrc: img.getAttribute('data-zoom-image'),
                            dataThickboxSrc: img.getAttribute('data-image-thickbox-src'),
                            dataOriginalSrc: img.getAttribute('data-original-src'),
                        pictureBest: best
                        };
                    }
                    
                    // Extract main images
                    mainSelectors.forEach(selector => {
                        const imgs = document.querySelectorAll(selector);
                        imgs.forEach(img => {
                            if (img.src || img.getAttribute('data-src')) {
                                images.mainImages.push(getImageInfo(img));
                            }
                        });
                    });
                    
                    // Extract thumbnails
                    thumbSelectors.forEach(selector => {
                        const imgs = document.querySelectorAll(selector);
                        imgs.forEach(img => {
                            if (img.src || img.getAttribute('data-src')) {
                                images.thumbnails.push(getImageInfo(img));
                            }
                        });
                    });
                    
                    // Extract from product containers
                    containerSelectors.forEach(selector => {
                        const containers = document.querySelectorAll(selector);
                        containers.forEach(container => {
                            const imgs = container.querySelectorAll('img');
                            imgs.forEach(img => {
                                if (img.src || img.getAttribute('data-src')) {
                                    images.allProductImages.push(getImageInfo(img));
                                }
                            });
                            
                            // Store container HTML for context
                            if (imgs.length > 0) {
                                images.imageContainers.push({
                                    html: container.outerHTML,
                                    selector: selector,
                                    imageCount: imgs.length
                                });
                            }
                        });
                    });
                    
                    // Smart fallback: Find all product-related images
                    if (images.mainImages.length + images.thumbnails.length + images.allProductImages.length < 3) {
                        // Look for images in the main content area first
                        const productAreas = [
                            document.querySelector('main'),
                            document.querySelector('.product'),
                            document.querySelector('#product'),
                            document.querySelector('.content'),
                            document.querySelector('#content'),
                            document.body
                        ].filter(area => area);
                        
                        for (const area of productAreas) {
                            const allImgs = area.querySelectorAll('img');
                            allImgs.forEach(img => {
                                // Enhanced filtering for product images
                                if (img.src && img.src.startsWith('http') && 
                                    img.width > 100 && img.height > 100 &&
                                    !img.src.includes('icon') && 
                                    !img.src.includes('logo') &&
                                    !img.src.includes('avatar') &&
                                    !img.src.includes('banner') &&
                                    !img.className.includes('logo') &&
                                    !img.className.includes('icon') &&
                                    !img.alt.toLowerCase().includes('logo')) {
                                    
                                    // Collect ALL possible image URLs from this element
                                    const imgInfo = getImageInfo(img);
                                    
                                    // Add multiple versions of the same image if they exist
                                    const allUrls = [
                                        imgInfo.src,
                                        imgInfo.dataSrc,
                                        imgInfo.dataLargeSrc,
                                        imgInfo.dataZoomSrc,
                                        img.getAttribute('data-image-medium-src'),
                                        img.getAttribute('data-image-thickbox-src'),
                                        img.getAttribute('data-original-src'),
                                        img.getAttribute('data-full-src'),
                                        img.getAttribute('data-large'),
                                        img.getAttribute('data-zoom'),
                                        img.getAttribute('data-big')
                                    ].filter(url => url && url.startsWith('http'));
                                    
                                    // Create separate entries for different quality versions
                                    allUrls.forEach(url => {
                                        if (url !== imgInfo.src) {
                                            images.allProductImages.push({
                                                ...imgInfo,
                                                src: url,
                                                quality: url.includes('large') || url.includes('big') || url.includes('zoom') ? 'high' : 'medium'
                                            });
                                        }
                                    });
                                    
                                    images.allProductImages.push(imgInfo);
                                }
                            });
                            
                            // If we found images in this area, prioritize them
                            if (images.allProductImages.length > 0) break;
                        }
                    }
                    
                    return images;
                }
            """)
            
            # Log what we found
            logger.info(f"Raw image extraction results:")
            logger.info(f"  Main images count: {len(image_data.get('mainImages', []))}")
            logger.info(f"  Thumbnails count: {len(image_data.get('thumbnails', []))}")
            logger.info(f"  Container images count: {len(image_data.get('allProductImages', []))}")
            logger.info(f"  Image containers count: {len(image_data.get('imageContainers', []))}")
            # Print raw URLs for backend visibility
            raw_main_urls = [img.get('src') or img.get('dataSrc') for img in image_data.get('mainImages', [])]
            raw_thumb_urls = [img.get('src') or img.get('dataSrc') for img in image_data.get('thumbnails', [])]
            raw_all_urls = [img.get('src') or img.get('dataSrc') for img in image_data.get('allProductImages', [])]
            print(f"[ImageExtractor-RAW] mainImages URLs: {raw_main_urls}")
            print(f"[ImageExtractor-RAW] thumbnails URLs: {raw_thumb_urls}")
            print(f"[ImageExtractor-RAW] allProductImages URLs: {raw_all_urls}")
            
            # Process and deduplicate images
            processed_images = self._process_extracted_images(image_data, product_name)
            
            logger.info(f"After processing images:")
            logger.info(f"  Main image URL: {processed_images['images']['urlMainimage']}")
            logger.info(f"  Other images count: {len(processed_images['images']['otherMainImages'])}")
            logger.info(f"  Other image URLs: {processed_images['images']['otherMainImages']}")
            # Also print to stdout for immediate visibility
            print(f"[ImageExtractor] Extracted main image: {processed_images['images']['urlMainimage']}")
            print(f"[ImageExtractor] Extracted other images: {processed_images['images']['otherMainImages']}")
            
            return processed_images
            
        except Exception as e:
            logger.error(f"Failed to extract product images: {e}")
            return {
                "images": {
                    "urlMainimage": None,
                    "otherMainImages": []
                },
                "relevantHtmlProductContext": "",
                "schema.org": None
            }
    
    def _process_extracted_images(self, image_data: Dict, product_name: str = None) -> Dict[str, Any]:
        """Process and organize extracted images."""
        # If no explicit mainImages found, promote high-quality container images as main candidates
        if not image_data.get('mainImages'):
            fallback_mains = [img for img in image_data.get('allProductImages', [])
                              if img.get('dataMediumSrc') or img.get('dataLargeSrc') \
                                 or img.get('dataThickboxSrc') or img.get('dataOriginalSrc')]
            if fallback_mains:
                logger.info(f"Promoting {len(fallback_mains)} container images to mainImages by data-* attributes")
                image_data['mainImages'] = fallback_mains
        all_images = []
        
        # Collect all images with metadata
        for img in image_data.get('mainImages', []):
            all_images.append({
                **img,
                'type': 'main',
                'priority': 10
            })
        
        for img in image_data.get('thumbnails', []):
            all_images.append({
                **img,
                'type': 'thumbnail', 
                'priority': 5
            })
        
        for img in image_data.get('allProductImages', []):
            all_images.append({
                **img,
                'type': 'container',
                'priority': 7
            })
        
        # Deduplicate images by URL
        unique_images = {}
        for img in all_images:
            # Get the best quality URL
            img_url = self._get_best_image_url(img)
            if img_url and img_url not in unique_images:
                unique_images[img_url] = img
            elif img_url and img_url in unique_images:
                # Keep the higher priority image
                if img['priority'] > unique_images[img_url]['priority']:
                    unique_images[img_url] = img
        
        # Sort images by quality and relevance
        sorted_images = sorted(
            unique_images.values(),
            key=lambda x: self._calculate_image_score(x, product_name),
            reverse=True
        )
        
        # Extract main image and others using the best URLs
        main_image = self._get_best_image_url(sorted_images[0]) if sorted_images else None
        other_images = [self._get_best_image_url(img) for img in sorted_images[1:] if self._get_best_image_url(img)] if len(sorted_images) > 1 else []
        
        # Get relevant HTML context
        html_context = self._extract_html_context(image_data.get('imageContainers', []))
        
        return {
            "images": {
                "urlMainimage": main_image,
                "otherMainImages": other_images
            },
            "relevantHtmlProductContext": html_context,
            "schema.org": None  # Will be filled by the main scraper
        }
    
    def _get_best_image_url(self, img: Dict) -> Optional[str]:
        """Get the highest quality image URL from available sources."""
        # Priority order for image URLs (highest quality first)
        # Include pictureBest (from <picture> srcset) as highest priority
        url_candidates = [
            img.get('pictureBest'),           # Best from picture srcset
            img.get('dataZoomSrc'),           # Zoom images
            img.get('dataThickboxSrc'),       # Thickbox images
            img.get('dataOriginalSrc'),       # Original images
            img.get('dataLargeSrc'),          # Large images
            img.get('dataMediumSrc'),         # Medium images
            img.get('dataSrc'),               # Lazy-loaded images
            img.get('src')                    # Standard src
        ]
        
        for url in url_candidates:
            if url and url.startswith(('http', '//')):
                # Strip low-res blur placeholders (e.g., &w=10&blur=10)
                clean_url = re.sub(r'&w=\d+&blur=\d+', '', url)
                return clean_url
        return None
    
    def _calculate_image_score(self, img: Dict, product_name: str = None) -> float:
        """Calculate image quality/relevance score."""
        score = 0
        
        # Base score by type
        type_scores = {
            'main': 100,
            'container': 70, 
            'thumbnail': 30
        }
        score += type_scores.get(img['type'], 50)
        
        # Size score (prefer larger images)
        width = img.get('width', 0)
        height = img.get('height', 0)
        area = width * height
        
        if area > 400000:  # Large images (e.g., 800x500+)
            score += 50
        elif area > 150000:  # Medium images (e.g., 500x300+)
            score += 30
        elif area > 50000:   # Small images (e.g., 300x200+)
            score += 10
        
        # Quality indicators in URL
        img_url = img.get('src', '')
        for keyword in self.quality_keywords:
            if keyword in img_url.lower():
                score += 20
                break
        
        # Product name relevance (if available)
        if product_name:
            img_alt = img.get('alt', '').lower()
            name_words = product_name.lower().split()
            matching_words = sum(1 for word in name_words if len(word) > 3 and word in img_alt)
            if matching_words > 0:
                score += matching_words * 15
        
        # Avoid icons, logos, and small images
        if any(term in img_url.lower() for term in ['icon', 'logo', 'sprite', 'button']):
            score -= 30
        
        if width < 100 or height < 100:
            score -= 20
        
        return score
    
    def _extract_html_context(self, containers: List[Dict]) -> str:
        """Extract relevant HTML context from image containers."""
        if not containers:
            return ""
        
        # Find the most relevant container (most images)
        best_container = max(containers, key=lambda x: x.get('imageCount', 0))
        
        # Clean and return the HTML
        html = best_container.get('html', '')
        
        # Basic HTML cleaning (remove script tags, etc.)
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Limit HTML size
        if len(html) > 5000:
            html = html[:5000] + "..."
        
        return html