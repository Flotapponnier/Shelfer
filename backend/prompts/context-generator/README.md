# Context Generator Framework

> **Multi-tier prompt system for extracting structured product context from HTML content to enrich schema.org Product fields**

## Overview

This framework provides 6 specialized context generators that extract different types of product information from HTML content. Each generator is optimized for specific schema.org fields and implements research-backed prompt engineering techniques for high accuracy extraction.

**Architecture**: Tier 1 Context Generators → Tier 2 Field Extractors → Tier 3 Validators

## Quick Start

```python
from product_context_generator import PRODUCT_CONTEXT_GENERATOR_PROMPT, validate_product_context

# 1. Format prompt with HTML content
html_content = "<h1>Nike Air Max 90</h1><div>Premium athletic sneakers...</div>"
prompt = PRODUCT_CONTEXT_GENERATOR_PROMPT.format(html_content=html_content)

# 2. Send to LLM (your implementation)
context_output = your_llm_call(prompt)

# 3. Validate output
validation = validate_product_context(context_output)
if validation["is_valid"]:
    print(f"Confidence: {validation['confidence_score']}")
```

## Context Generators

### 🏷️ Product Context Generator
**File**: `product_context_generator.py`  
**Purpose**: Core product identity, categories, and general specifications

**Primary Fields**: `name`, `description`, `category`  
**Secondary Fields**: `brand`, `audience`, `additionalProperty`  
**Token Budget**: 1,200 tokens

**When to Use**: Always - this is the foundation context for any product  
**Best For**: Product titles, descriptions, category classification, target audience

```python
from product_context_generator import (
    PRODUCT_CONTEXT_GENERATOR_PROMPT,
    PRODUCT_CONTEXT_GENERATOR_COMPACT,  # 40% fewer tokens
    validate_product_context
)

# Use compact version for simple products
if product_complexity == "simple":
    prompt = PRODUCT_CONTEXT_GENERATOR_COMPACT.format(html_content=html)
```

**Expected Output Format**:
```
Product Name: Nike Air Max 90 Premium Sneakers
Brand: Nike
Product Category: Athletic Footwear - Running Shoes
Description: Premium athletic sneakers with visible Air Max cushioning
Target Audience: Athletes, fitness enthusiasts, casual wear
```

---

### 💰 Commercial Context Generator
**File**: `commercial_context_generator.py`  
**Purpose**: Pricing, availability, offers, and commercial terms

**Primary Fields**: `offers`, `price`, `availability`  
**Secondary Fields**: `seller`, `warranty`, `shippingDetails`  
**Token Budget**: 1,100 tokens

**When to Use**: For any product with pricing or purchase information  
**Best For**: E-commerce sites, product listings with prices

```python
from commercial_context_generator import (
    COMMERCIAL_CONTEXT_GENERATOR_PROMPT,
    validate_commercial_context,
    extract_pricing_data,  # Helper function for price parsing
    analyze_availability_status  # Helper for stock analysis
)

# Extract structured pricing data
pricing_data = extract_pricing_data(context_output)
# Returns: {"price": 129.99, "currency": "USD", "discount": 20}
```

**Expected Output Format**:
```
Price: $129.99 USD
Original Price: $149.99 USD (13% discount)
Availability: In Stock
Seller: Nike Official Store
Shipping: Free shipping on orders over $50
Return Policy: 30-day returns accepted
```

---

### 🏢 Brand Context Generator
**File**: `brand_context_generator.py`  
**Purpose**: Brand identity, heritage, positioning, and country information

**Primary Fields**: `brand`, `manufacturer`  
**Secondary Fields**: `countryOfOrigin`, `brand.logo`  
**Token Budget**: 1,000 tokens

**When to Use**: When brand context is important for positioning or compliance  
**Best For**: Brand-focused products, luxury goods, origin-sensitive items

```python
from brand_context_generator import (
    BRAND_CONTEXT_GENERATOR_PROMPT,
    validate_brand_context,
    extract_brand_hierarchy,  # Helper for brand relationships
    validate_country_names    # Helper for country validation
)

# Extract brand hierarchy (parent brand, sub-brands)
brand_hierarchy = extract_brand_hierarchy(context_output)
```

**Expected Output Format**:
```
Brand Name: Nike
Parent Company: Nike, Inc.
Brand Category: Athletic apparel and footwear
Brand Heritage: American sportswear brand founded 1964
Country of Origin: United States
Brand Positioning: Premium athletic performance
```

---

### 👥 UX Context Generator
**File**: `ux_context_generator.py`  
**Purpose**: Customer reviews, ratings, sentiment analysis, and feedback

**Primary Fields**: `aggregateRating`, `review`, `negativeNotes`, `positiveNotes`  
**Secondary Fields**: `description`, `offers.itemCondition`  
**Token Budget**: 1,400 tokens

**When to Use**: When customer feedback data is available  
**Best For**: Products with reviews, ratings, testimonials

```python
from ux_context_generator import (
    UX_CONTEXT_GENERATOR_PROMPT,
    validate_ux_context,
    extract_rating_data,      # Helper for rating extraction
    analyze_sentiment_themes  # Helper for theme analysis
)

# Handle "no reviews" scenario
validation = validate_ux_context(context_output)
if validation["extracted_fields"]["status"] == "insufficient_data":
    # Skip UX context for this product
    pass
```

**Expected Output Format**:
```
Aggregate Rating: 4.5 out of 5 stars
Total Reviews: 127
Positive Themes: Comfort, Durability, Style, Value for money
Negative Themes: Sizing runs small, Limited color options
Overall Sentiment: Highly positive with minor sizing concerns
Customer Satisfaction: High (4.5/5 rating with substantial review volume)
```

---

### 🔧 Technical Context Generator
**File**: `technical_context_generator.py`  
**Purpose**: Materials, specifications, compliance, and manufacturing data

**Primary Fields**: `material`, `nsn`, `countryOfLastProcessing`  
**Secondary Fields**: `mpn`, `gtin`, `productID`, `model`, `itemCondition`  
**Token Budget**: 1,200 tokens

**When to Use**: For products with technical specifications or material details  
**Best For**: Technical products, manufactured goods, compliance-sensitive items

```python
from technical_context_generator import (
    TECHNICAL_CONTEXT_GENERATOR_PROMPT,
    validate_technical_context,
    extract_material_composition,  # Helper for material analysis
    extract_country_information,   # Helper for origin tracking
    extract_product_identifiers    # Helper for ID extraction
)

# Extract material percentages
materials = extract_material_composition(context_output)
# Returns: {"primary_material": "Cotton", "material_percentage": {"Cotton": 65, "Polyester": 35}}
```

**Expected Output Format**:
```
Materials: 65% Cotton, 35% Polyester blend
Country of Origin: Bangladesh
Product Identifiers: SKU: NK-AM90-001, UPC: 123456789012
Item Condition: New
Technical Features: Pre-shrunk, Machine washable
Certifications: Oeko-Tex Standard 100
```

---

### 🎨 Visual Context Generator
**File**: `visual_context_generator.py`  
**Purpose**: Colors, sizes, dimensions, and visual attributes

**Primary Fields**: `color`, `size`, `height`, `width`, `depth`, `weight`  
**Secondary Fields**: `name`, `description`, `category`, `pattern`  
**Token Budget**: 1,300 tokens

**When to Use**: For products with visual variants or dimensional specifications  
**Best For**: Fashion, furniture, products with color/size options

```python
from visual_context_generator import (
    VISUAL_CONTEXT_GENERATOR_PROMPT,
    validate_visual_context,
    extract_color_information,  # Helper for color parsing
    extract_size_information,   # Helper for size/dimension data
    standardize_color_names     # Helper for color standardization
)

# Extract color with hex codes
colors = extract_color_information(context_output)
# Returns: {"available_colors": ["Navy Blue"], "color_codes": {"Navy Blue": "#1e3a8a"}}
```

**Expected Output Format**:
```
Available Colors: Black, White, Navy Blue (#1e3a8a)
Size Options: US Men's 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 12
Dimensions: Length: 12 inches, Width: 4.5 inches
Style Description: Low-top athletic sneakers with visible Air Max cushioning
```

## Usage Patterns

### 1. Complete Product Analysis
```python
def analyze_product_page(html_content: str) -> dict:
    """Run all relevant context generators on a product page."""
    contexts = {}
    
    # Always run product context (foundation)
    contexts['product'] = run_generator('product', html_content)
    
    # Run other generators based on content availability
    if has_pricing_info(html_content):
        contexts['commercial'] = run_generator('commercial', html_content)
    
    if has_brand_info(html_content):
        contexts['brand'] = run_generator('brand', html_content)
    
    if has_reviews(html_content):
        contexts['ux'] = run_generator('ux', html_content)
    
    if has_technical_specs(html_content):
        contexts['technical'] = run_generator('technical', html_content)
    
    if has_visual_variants(html_content):
        contexts['visual'] = run_generator('visual', html_content)
    
    return contexts
```

### 2. Token-Optimized Usage
```python
def smart_context_generation(html_content: str, token_budget: int = 7200) -> dict:
    """Optimize context generation based on token budget."""
    
    # Analyze HTML complexity
    complexity = analyze_html_complexity(html_content)
    
    # Use compact versions for simple products
    if complexity == "simple" and token_budget < 5000:
        return {
            'product': run_compact_generator('product', html_content),
            'commercial': run_compact_generator('commercial', html_content),
            'visual': run_compact_generator('visual', html_content)
        }
    
    # Use full versions for complex products
    return run_all_generators(html_content)
```

### 3. Validation-First Approach
```python
def validated_context_extraction(generator_name: str, html_content: str) -> dict:
    """Extract context with validation and retry logic."""
    
    # Try full prompt first
    context = run_generator(generator_name, html_content)
    validation = validate_context(generator_name, context)
    
    if validation["is_valid"] and validation["confidence_score"] > 0.8:
        return {"context": context, "validation": validation}
    
    # Retry with compact version if validation fails
    context_compact = run_compact_generator(generator_name, html_content)
    validation_compact = validate_context(generator_name, context_compact)
    
    return {"context": context_compact, "validation": validation_compact}
```

## Performance Guidelines

### Token Budgets
| Generator | Full Prompt | Compact Version | Savings |
|-----------|-------------|-----------------|---------|
| Product | 1,200 tokens | 600 tokens | 50% |
| Commercial | 1,100 tokens | 550 tokens | 50% |
| Brand | 1,000 tokens | 500 tokens | 50% |
| UX | 1,400 tokens | 700 tokens | 50% |
| Technical | 1,200 tokens | 600 tokens | 50% |
| Visual | 1,300 tokens | 650 tokens | 50% |
| **Total** | **7,200 tokens** | **3,600 tokens** | **50%** |

### Confidence Thresholds
- **High Confidence**: 0.8+ (use output directly)
- **Medium Confidence**: 0.6-0.8 (review before use)
- **Low Confidence**: <0.6 (retry with different prompt or skip)

### Processing Order
1. **Product Context** (always first - provides foundation)
2. **Visual Context** (informs other generators about variants)
3. **Commercial Context** (pricing affects brand positioning)
4. **Brand Context** (contextualizes commercial offers)
5. **Technical Context** (specifications support claims)
6. **UX Context** (validates claims made by other contexts)

## Testing

### Run All Tests
```bash
cd backend/prompts/context-generator/
python test_context_generators.py
```

### Individual Generator Testing
```python
from test_context_generators import ContextGeneratorTester

tester = ContextGeneratorTester()

# Test specific generator
result = tester.test_individual_generator('product', html_content)
print(f"Confidence: {result['validation_result']['confidence_score']}")
```

### Custom Test Cases
```python
# Create custom HTML test case
html_test = """
<h1>Custom Product Name</h1>
<div class="price">$99.99</div>
<div class="colors">Red, Blue, Green</div>
"""

# Test against specific generator
result = tester.test_individual_generator('visual', html_test)
```

## Error Handling

### Common Issues & Solutions

**1. "No sufficient context found"**
```python
if "no sufficient" in context_output.lower():
    # This is normal - generator found no relevant data
    # Skip this context type for this product
    return None
```

**2. Low confidence scores**
```python
validation = validate_context(generator_name, context_output)
if validation["confidence_score"] < 0.6:
    # Try compact version or different approach
    return retry_with_compact_version()
```

**3. Token budget exceeded**
```python
if estimated_tokens > generator["token_budget"]:
    # Use compact version automatically
    return run_compact_generator(generator_name, html_content)
```

## Integration Examples

### FastAPI Integration
```python
from fastapi import FastAPI
from .context_generator import run_all_generators

app = FastAPI()

@app.post("/extract-context")
async def extract_context(html: str):
    contexts = run_all_generators(html)
    return {
        "contexts": contexts,
        "field_coverage": calculate_coverage(contexts),
        "confidence_scores": get_confidence_scores(contexts)
    }
```

### Batch Processing
```python
def process_product_batch(html_list: List[str]) -> List[dict]:
    """Process multiple products efficiently."""
    results = []
    
    for html in html_list:
        try:
            contexts = analyze_product_page(html)
            results.append({"success": True, "contexts": contexts})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    
    return results
```

## Best Practices

### ✅ Do:
- Always run Product Context Generator first
- Validate outputs before using in production
- Use compact versions for simple products to save tokens
- Check confidence scores and retry if low
- Handle "no sufficient context" responses gracefully

### ❌ Don't:
- Run UX Context Generator on products without reviews
- Ignore validation results
- Use generators on empty or minimal HTML
- Exceed token budgets without fallback plans
- Mix context generators from different product pages

## Troubleshooting

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug information
result = run_generator('product', html_content, debug=True)
```

### Performance Analysis
```python
# Measure token usage
token_count = estimate_tokens(prompt)
print(f"Estimated tokens: {token_count}")

# Measure processing time
import time
start = time.time()
context = run_generator('visual', html_content)
print(f"Processing time: {time.time() - start:.2f}s")
```

---

## Support

For questions or issues:
1. Check the validation functions for expected output formats
2. Review test cases in `test_context_generators.py`
3. Consult the detailed task documentation in `/tasks/`

**Last Updated**: November 2024  
**Framework Version**: 1.0  
**Python Compatibility**: 3.8+ 