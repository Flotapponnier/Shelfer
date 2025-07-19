"""
Commercial Context Generator Prompt
==================================

Tier 1 Context Generator for extracting comprehensive commercial information
including pricing, availability, purchase conditions, and return policies.
This prompt implements research-backed techniques for high-accuracy extraction.

Expected Performance Improvements:
- System Role Assignment: 10-50% accuracy improvement
- Chain-of-Thought: 50-100% accuracy improvement  
- Few-Shot Learning: 26-47% performance gains
- Emotion Prompting: 8-115% performance boost

Primary Context For Fields:
- offers.price, offers.priceCurrency, offers.availability
- offers.itemCondition, hasMerchantReturnPolicy
"""

COMMERCIAL_CONTEXT_GENERATOR_PROMPT = """# System Role
You are a **specialized e-commerce pricing and availability analyst** with 15+ years of experience in extracting commercial information from product pages. You excel at identifying pricing structures, availability status, shipping details, and purchase conditions across diverse e-commerce platforms and international markets.

## Task Definition
Your task is to analyze HTML content and extract comprehensive **Commercial Context** using this systematic approach:

1. **Identify Pricing Information**: Extract prices, currencies, discounts, and pricing variations
2. **Determine Availability Status**: Analyze stock indicators, availability messages, and inventory data
3. **Extract Purchase Conditions**: Identify item conditions, shipping details, and return policies
4. **Analyze Offer Structure**: Understand variant pricing and conditional offers
5. **Compile Commercial Data**: Create structured commercial context summary

## Context & Specifics
This extraction is **essential for accurate e-commerce schema.org markup** and directly impacts product discoverability in search engines and shopping platforms. Accurate commercial context extraction improves conversion rates and customer experience by providing clear purchase information.

**Business Impact**: Your precise commercial data extraction enables proper schema.org offers markup including price, currency, availability, item condition, and return policy information that builds customer trust and improves search rankings.

## Examples (Few-Shot)

### Example 1
**Input HTML**: `<span class="price">€29.99</span><div class="stock">In Stock</div><p class="condition">New</p><div class="shipping">Free shipping over €50</div><a href="/returns">30-day return policy</a>`

**Output Commercial Context**:
```
Price: 29.99
Currency: EUR
Availability: In Stock
Item Condition: New
Shipping: Free shipping over €50
Return Policy: 30-day return policy
Stock Status: Available
```

### Example 2
**Input HTML**: `<div class="price-section"><span class="original">$199.99</span><span class="sale">$149.99</span></div><div class="availability">Only 3 left in stock</div><p class="warranty">2-year warranty included</p><div class="condition">Refurbished</div>`

**Output Commercial Context**:
```
Original Price: 199.99
Sale Price: 149.99
Currency: USD
Availability: Limited Stock (3 remaining)
Item Condition: Refurbished
Warranty: 2-year warranty included
Stock Status: Low inventory warning
```

### Example 3
**Input HTML**: `<span class="out-of-stock">Temporarily Out of Stock</span><div class="notify">Email when available</div><p class="msrp">MSRP: £89.99</p><div class="returns">No returns on clearance items</div>`

**Output Commercial Context**:
```
Price: 89.99 (MSRP)
Currency: GBP
Availability: Out of Stock (Temporary)
Restock Option: Email notification available
Item Condition: Not specified
Return Policy: No returns on clearance items
Stock Status: Temporarily unavailable
```

### Example 4
**Input HTML**: `<div class="pricing">Contact for pricing</div><div class="availability">Made to order - 2-3 weeks delivery</div><p class="condition">Brand new</p>`

**Output Commercial Context**:
```
Price: Contact for pricing
Currency: Not specified
Availability: Made to order (2-3 weeks delivery)
Item Condition: Brand new
Stock Status: Custom order
```

### Example 5
**Input HTML**: `<div class="membership-price">Members: $79.99 | Non-members: $99.99</div><span class="currency">USD</span><div class="stock-info">In stock at 5 locations</div>`

**Output Commercial Context**:
```
Member Price: 79.99
Regular Price: 99.99
Currency: USD
Availability: In Stock (5 locations)
Item Condition: Not specified
Stock Status: Available at multiple locations
```

### Example 6
**Input HTML**: `<div class="product-info">Product description here</div><nav>Home > About</nav><footer>Contact us</footer>`

**Output Commercial Context**:
```
No sufficient commercial context found
```

## Critical Reminders
- Extract ONLY commercial information explicitly present in the HTML content
- Preserve exact price values including decimal places and currency symbols
- Map availability text to clear status descriptions (In Stock, Out of Stock, Limited Stock, etc.)
- If multiple prices exist (sale, MSRP, member pricing), capture all pricing information with clear labels
- Return "No sufficient commercial context found" if no pricing or availability data is present
- Distinguish between permanent and temporary availability issues when indicated
- Note shipping conditions and return policies when explicitly mentioned
- Do not hallucinate pricing or availability information not clearly stated
- Prefer explicit commercial data over general marketing language

**Input HTML Content**: {html_content}"""

# Alternative shorter version for token-constrained scenarios
COMMERCIAL_CONTEXT_GENERATOR_COMPACT = """You are an expert e-commerce pricing analyst. Extract commercial information from the HTML below and format as structured commercial context.

Return format:
```
Price: [price value]
Currency: [currency code/symbol]
Availability: [stock status]
Item Condition: [new/used/refurbished/etc.]
Return Policy: [return conditions if mentioned]
Stock Status: [detailed availability info]
```

If no commercial information is available, return: "No sufficient commercial context found"

HTML Content: {html_content}"""

# Context generator configuration
COMMERCIAL_CONTEXT_CONFIG = {
    "max_tokens": 1200,
    "temperature": 0.05,  # Very low temperature for precise pricing extraction
    "timeout": 25,
    "retry_attempts": 2,
    "validation_required": True,
    "confidence_threshold": 0.6
}

def validate_commercial_context(context_output: str) -> dict:
    """
    Validate the commercial context output format and completeness.
    
    Args:
        context_output: The raw output from the commercial context generator
        
    Returns:
        dict: Validation result with status and extracted fields
    """
    validation_result = {
        "is_valid": False,
        "extracted_fields": {},
        "missing_fields": [],
        "confidence_score": 0.0,
        "errors": []
    }
    
    # Check for "no sufficient commercial context" response
    if "no sufficient commercial context found" in context_output.lower():
        validation_result["is_valid"] = True
        validation_result["confidence_score"] = 1.0
        validation_result["extracted_fields"]["status"] = "insufficient_data"
        return validation_result
    
    # Expected fields in commercial context (at least one required)
    core_fields = ["price", "currency", "availability"]
    optional_fields = ["item condition", "return policy", "stock status"]
    
    # Parse structured output
    lines = context_output.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if field_value and field_value != "Not specified":
                validation_result["extracted_fields"][field_name] = field_value
    
    # Check for core commercial fields
    found_core_fields = 0
    for field in core_fields:
        if any(field in key for key in validation_result["extracted_fields"].keys()):
            found_core_fields += 1
        else:
            validation_result["missing_fields"].append(field)
    
    # Special validation for pricing
    has_price_info = any("price" in key for key in validation_result["extracted_fields"].keys())
    has_availability_info = any("availability" in key or "stock" in key for key in validation_result["extracted_fields"].keys())
    
    # Calculate confidence based on core field presence
    if has_price_info and has_availability_info:
        validation_result["confidence_score"] = 0.9
    elif has_price_info or has_availability_info:
        validation_result["confidence_score"] = 0.7
    else:
        validation_result["confidence_score"] = 0.3
        validation_result["errors"].append("No core commercial information (price or availability) found")
    
    validation_result["is_valid"] = validation_result["confidence_score"] >= 0.6
    
    # Validate currency format if present
    currency_fields = [k for k in validation_result["extracted_fields"].keys() if "currency" in k]
    if currency_fields:
        currency_value = validation_result["extracted_fields"][currency_fields[0]]
        if currency_value.lower() not in ["usd", "eur", "gbp", "jpy", "cad", "aud", "$", "€", "£", "¥", "not specified"]:
            # Check if it's a proper currency format
            if len(currency_value) > 5 and "currency" not in currency_value.lower():
                validation_result["errors"].append(f"Unusual currency format: {currency_value}")
    
    return validation_result

def extract_price_value(price_string: str) -> tuple:
    """
    Extract numeric price value and currency from price string.
    
    Args:
        price_string: Raw price string from context
        
    Returns:
        tuple: (numeric_value, currency_code) or (None, None) if invalid
    """
    import re
    
    if not price_string or price_string.lower() in ["contact for pricing", "not specified"]:
        return None, None
    
    # Common currency patterns
    currency_patterns = {
        r'€': 'EUR',
        r'\$': 'USD', 
        r'£': 'GBP',
        r'¥': 'JPY'
    }
    
    # Extract numeric value
    price_match = re.search(r'(\d+(?:\.\d{2})?)', price_string)
    if not price_match:
        return None, None
    
    numeric_value = float(price_match.group(1))
    
    # Extract currency
    currency_code = None
    for pattern, code in currency_patterns.items():
        if re.search(pattern, price_string):
            currency_code = code
            break
    
    # Check for ISO currency codes
    iso_match = re.search(r'\b([A-Z]{3})\b', price_string)
    if iso_match and not currency_code:
        currency_code = iso_match.group(1)
    
    return numeric_value, currency_code 