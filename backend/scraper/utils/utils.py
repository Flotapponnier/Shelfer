import logging
import os
from datetime import datetime
from typing import Optional 
from playwright.async_api import Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
]


def extract_links_with_context_js() -> str:
    """
    Generate JavaScript code for extracting links with HTML context, including parent, sibling, children, and grandchildren text contents.
    
    Returns:
        str: JavaScript code that can be executed in the browser
    """
    return """
        () => {
            function getTextAndDescendants(element, maxDepth = 2, depth = 0) {
                if (!element || depth > maxDepth) return [];
                let texts = [];
                if (element.textContent && element.textContent.trim()) {
                    texts.push(element.textContent.trim());
                }
                if (element.children && element.children.length > 0 && depth < maxDepth) {
                    for (let child of element.children) {
                        texts = texts.concat(getTextAndDescendants(child, maxDepth, depth + 1));
                    }
                }
                return texts;
            }

            try {
                const links = [];
                const anchors = document.querySelectorAll('a[href]');
                for (let anchor of anchors) {
                    const href = anchor.getAttribute('href');
                    if (href && href.trim()) {
                        let absoluteUrl;
                        try {
                            absoluteUrl = new URL(href.trim(), window.location.href).href;
                        } catch (e) {
                            continue;
                        }
                        // Get anchor context
                        const context = {
                            tagName: anchor.tagName,
                            text: anchor.textContent?.trim() || '',
                            title: anchor.title || '',
                            class: anchor.getAttribute('class') || '',
                            id: anchor.getAttribute('id') || '',
                            href: href,
                            dataAttributes: {},
                        };
                        let dataCount = 0;
                        for (let attr of anchor.attributes) {
                            if (dataCount >= 5) break;
                            if (attr.name.startsWith('data-')) {
                                context.dataAttributes[attr.name] = attr.value;
                                dataCount++;
                            }
                        }
                        // Parent context
                        const parent = anchor.parentElement;
                        context.parentText = parent ? parent.textContent?.trim() || '' : '';
                        // Sibling contexts
                        context.siblingTexts = [];
                        if (parent) {
                            for (let sibling of parent.children) {
                                if (sibling !== anchor) {
                                    context.siblingTexts.push({
                                        text: sibling.textContent?.trim() || '',
                                        childrenTexts: getTextAndDescendants(sibling, 1, 1),
                                        grandchildrenTexts: getTextAndDescendants(sibling, 2, 2)
                                    });
                                }
                            }
                        }
                        // Children and grandchildren of anchor
                        context.childrenTexts = getTextAndDescendants(anchor, 1, 1);
                        context.grandchildrenTexts = getTextAndDescendants(anchor, 2, 2);
                        // Children and grandchildren of parent
                        context.parentChildrenTexts = [];
                        if (parent) {
                            for (let child of parent.children) {
                                context.parentChildrenTexts.push({
                                    text: child.textContent?.trim() || '',
                                    childrenTexts: getTextAndDescendants(child, 1, 1),
                                    grandchildrenTexts: getTextAndDescendants(child, 2, 2)
                                });
                            }
                        }
                        links.push({
                            url: absoluteUrl,
                            context: context
                        });
                    }
                }
                return links;
            } catch (error) {
                console.error('Error in link extraction:', error);
                return [];
            }
        }
    """


async def take_error_screenshot(page: Page, url: str, error_type: str = "error") -> Optional[str]:
    """
    Take a screenshot when any error occurs and save it to the test results directory.
    Only works when SCREENSHOT_ENABLED=true environment variable is set.
    
    Args:
        page: Playwright page instance
        url: The URL that was being loaded when the error occurred
        error_type: Type of error (e.g., "timeout", "navigation", "networkidle", "page_closed")
    Returns:
        Path to the saved screenshot file, or None if screenshot failed or disabled
    """
    # Only take screenshots if explicitly enabled for testing
    if os.environ.get('SCREENSHOT_ENABLED', 'false').lower() != 'true':
        logger.debug(f"Screenshots disabled. Set SCREENSHOT_ENABLED=true to enable screenshot capture.")
        return None
    
    try:
        # Get the results directory from environment or use default
        results_dir = os.environ.get('SCREENSHOT_RESULTS_DIR', os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests', 'results', 'screenshots'))
        os.makedirs(results_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
        domain = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('?', '_').replace('&', '_')[:50]
        filename = f"{error_type}_{domain}_{timestamp}.png"
        
        screenshot_path = os.path.join(results_dir, filename)
        
        # Take screenshot
        await page.screenshot(path=screenshot_path, full_page=True)
        
        logger.info(f"📸 Screenshot saved for {error_type} error on {url}: {screenshot_path}")
        return screenshot_path
        
    except Exception as e:
        logger.error(f"❌ Failed to take screenshot for {error_type} error on {url}: {e}")
        return None



