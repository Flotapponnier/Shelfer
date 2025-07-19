"""
Brand Context Generator Prompt
==============================

Tier 1 Context Generator for extracting comprehensive brand and manufacturer
information including company background, origin country, and certifications.
This prompt implements research-backed techniques for high-accuracy extraction.

Expected Performance Improvements:
- System Role Assignment: 10-50% accuracy improvement
- Chain-of-Thought: 50-100% accuracy improvement  
- Few-Shot Learning: 26-47% performance gains
- Emotion Prompting: 8-115% performance boost

Primary Context For Fields:
- brand, manufacturer, countryOfLastProcessing

Secondary Context For Fields: 
- offers.priceCurrency, category, keywords, audience, additionalType,
- hasMerchantReturnPolicy, nsn
"""

BRAND_CONTEXT_GENERATOR_PROMPT = """# System Role
You are an **expert brand intelligence analyst** with 12+ years of experience in extracting and analyzing brand information from global e-commerce platforms. You specialize in identifying brand names, manufacturer details, company backgrounds, origin countries, and corporate relationships across diverse industries and international markets.

## Task Definition
Your task is to analyze HTML content and extract comprehensive **Brand Context** using this systematic approach:

1. **Identify Brand Information**: Extract brand names, logos, and brand positioning statements
2. **Determine Manufacturer Details**: Identify manufacturing companies and corporate relationships
3. **Extract Origin Information**: Find country of origin, manufacturing locations, and processing details
4. **Analyze Company Background**: Gather company history, certifications, and specializations
5. **Compile Brand Context**: Create structured brand and manufacturer summary

## Context & Specifics
This extraction is **crucial for accurate brand representation and trust building** in schema.org markup. Brand context directly impacts customer confidence, search visibility, and helps establish product authenticity and quality expectations.

**Business Impact**: Your precise brand analysis enables accurate schema.org brand markup, manufacturer identification, and origin tracking that builds customer trust, supports supply chain transparency, and improves search relevance for brand-specific queries.

## Examples (Few-Shot)

### Example 1
**Input HTML**: `<div class="brand-info"><img src="stoic-logo.png" alt="Stoic"><h2>Stoic Outdoor</h2></div><p class="about">Founded in Scandinavia, Stoic creates premium outdoor gear</p><div class="origin">Made in Portugal</div>`

**Output Brand Context**:
```
Brand Name: Stoic
Full Brand Name: Stoic Outdoor
Brand Description: Founded in Scandinavia, creates premium outdoor gear
Manufacturer: Stoic (same as brand)
Country of Origin: Scandinavia (founding location)
Country of Manufacturing: Portugal
Brand Specialization: Outdoor gear
Brand Positioning: Premium outdoor equipment
```

### Example 2
**Input HTML**: `<span class="brand">Sony</span><div class="company-info">Sony Corporation, Japanese multinational</div><p class="manufacturing">Manufactured by Sony Electronics Inc.</p><div class="origin">Made in Malaysia</div>`

**Output Brand Context**:
```
Brand Name: Sony
Full Company Name: Sony Corporation
Company Description: Japanese multinational corporation
Manufacturer: Sony Electronics Inc.
Country of Origin: Japan
Country of Manufacturing: Malaysia
Brand Specialization: Electronics
Corporate Structure: Multinational corporation
```

### Example 3
**Input HTML**: `<h1>Apple iPhone 15 Pro</h1><div class="legal">© Apple Inc. All rights reserved.</div><small class="origin">Designed by Apple in California. Assembled in China.</small>`

**Output Brand Context**:
```
Brand Name: Apple
Full Company Name: Apple Inc.
Design Location: California, USA
Country of Manufacturing: China
Manufacturer: Apple Inc. (designed by), Contract manufacturers (assembled)
Brand Specialization: Consumer electronics
Country of Last Processing: China
Brand Positioning: Premium technology
```

### Example 4
**Input HTML**: `<div class="brand-section"><img alt="Nike" src="nike-logo.jpg"><p>Nike, Inc. - Just Do It</p></div><div class="manufacturing">Manufactured by various partners worldwide</div><p class="sustainability">Committed to sustainable manufacturing</p>`

**Output Brand Context**:
```
Brand Name: Nike
Full Company Name: Nike, Inc.
Brand Slogan: Just Do It
Manufacturer: Various global manufacturing partners
Manufacturing Model: Contract manufacturing
Brand Values: Sustainability commitment
Brand Specialization: Athletic footwear and apparel
```

### Example 5
**Input HTML**: `<div class="product-line">Private Label Brand</div><div class="retailer">Exclusively by Target Corporation</div><p class="manufacturing">Made in Vietnam for Target</p>`

**Output Brand Context**:
```
Brand Name: Target Private Label
Brand Type: Private label/Store brand
Retailer: Target Corporation
Manufacturer: Contract manufacturer for Target
Country of Manufacturing: Vietnam
Brand Positioning: Exclusive retailer brand
Distribution: Target stores only
```

### Example 6
**Input HTML**: `<div class="artisan-made">Handcrafted by local artisans</div><div class="location">Small workshop in Tuscany, Italy</div><p class="tradition">Traditional Italian craftsmanship since 1952</p>`

**Output Brand Context**:
```
Brand Name: Not clearly specified (Artisan-made product)
Manufacturer: Local artisans in Tuscany
Country of Origin: Italy
Manufacturing Location: Tuscany, Italy
Manufacturing Type: Traditional handcraft
Established: Since 1952
Brand Positioning: Traditional Italian craftsmanship
```

### Example 7
**Input HTML**: `<div class="product-specs">Technical specifications here</div><nav>Categories</nav><footer>Contact info</footer>`

**Output Brand Context**:
```
No sufficient brand context found
```

## Critical Reminders
- Extract ONLY brand and manufacturer information explicitly present in the HTML content
- Distinguish between brand names and manufacturer names when they differ
- Preserve exact brand names, including special characters and capitalization
- Differentiate between country of origin (brand/design) and country of manufacturing
- Note corporate relationships (parent companies, subsidiaries, partnerships)
- Return "No sufficient brand context found" if no clear brand information is present
- Do not assume brand information from product categories or generic terms
- Capture certifications, sustainability claims, and brand values when mentioned
- Identify private label vs. national brand distinctions when evident
- Prefer explicit brand statements over inferred brand associations

**Input HTML Content**: {html_content}"""

# Alternative shorter version for token-constrained scenarios
BRAND_CONTEXT_GENERATOR_COMPACT = """You are an expert brand analyst. Extract brand and manufacturer information from the HTML below and format as structured brand context.

Return format:
```
Brand Name: [brand name]
Manufacturer: [manufacturing company]
Country of Origin: [brand origin country]
Country of Manufacturing: [where manufactured]
Brand Specialization: [product focus]
```

If no brand information is available, return: "No sufficient brand context found"

HTML Content: {html_content}"""

# Context generator configuration
BRAND_CONTEXT_CONFIG = {
    "max_tokens": 1300,
    "temperature": 0.1,  # Low temperature for consistent brand extraction
    "timeout": 30,
    "retry_attempts": 2,
    "validation_required": True,
    "confidence_threshold": 0.5
}

def validate_brand_context(context_output: str) -> dict:
    """
    Validate the brand context output format and completeness.
    
    Args:
        context_output: The raw output from the brand context generator
        
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
    
    # Check for "no sufficient brand context" response
    if "no sufficient brand context found" in context_output.lower():
        validation_result["is_valid"] = True
        validation_result["confidence_score"] = 1.0
        validation_result["extracted_fields"]["status"] = "insufficient_data"
        return validation_result
    
    # Expected fields in brand context
    core_fields = ["brand name"]
    important_fields = ["manufacturer", "country of origin", "country of manufacturing"]
    optional_fields = ["brand specialization", "brand positioning", "company description"]
    
    # Parse structured output
    lines = context_output.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if field_value and field_value != "Not clearly specified":
                validation_result["extracted_fields"][field_name] = field_value
    
    # Check for core brand fields
    has_brand_name = any("brand name" in key for key in validation_result["extracted_fields"].keys())
    has_manufacturer = any("manufacturer" in key for key in validation_result["extracted_fields"].keys())
    has_origin_info = any("country" in key or "origin" in key for key in validation_result["extracted_fields"].keys())
    
    # Calculate confidence score
    confidence_factors = []
    
    if has_brand_name:
        confidence_factors.append(0.4)  # Brand name is most important
    
    if has_manufacturer:
        confidence_factors.append(0.3)  # Manufacturer info is valuable
        
    if has_origin_info:
        confidence_factors.append(0.2)  # Origin information is helpful
    
    # Additional fields bonus
    additional_fields = len(validation_result["extracted_fields"]) - len(confidence_factors)
    if additional_fields > 0:
        confidence_factors.append(min(0.1, additional_fields * 0.02))
    
    validation_result["confidence_score"] = sum(confidence_factors)
    validation_result["is_valid"] = validation_result["confidence_score"] >= 0.5
    
    # Track missing core fields
    if not has_brand_name:
        validation_result["missing_fields"].append("brand name")
    if not has_manufacturer:
        validation_result["missing_fields"].append("manufacturer")
    if not has_origin_info:
        validation_result["missing_fields"].append("origin information")
    
    if not validation_result["is_valid"]:
        validation_result["errors"].append("Insufficient brand information extracted")
    
    return validation_result

def extract_brand_hierarchy(brand_context: str) -> dict:
    """
    Extract brand hierarchy and relationships from brand context.
    
    Args:
        brand_context: Raw brand context output
        
    Returns:
        dict: Structured brand hierarchy information
    """
    hierarchy = {
        "brand_name": None,
        "parent_company": None,
        "manufacturer": None,
        "is_private_label": False,
        "brand_type": "national_brand"  # default
    }
    
    lines = brand_context.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if "brand name" in field_name:
                hierarchy["brand_name"] = field_value
            elif "full company name" in field_name or "company name" in field_name:
                hierarchy["parent_company"] = field_value
            elif "manufacturer" in field_name:
                hierarchy["manufacturer"] = field_value
            elif "private label" in field_value.lower() or "store brand" in field_value.lower():
                hierarchy["is_private_label"] = True
                hierarchy["brand_type"] = "private_label"
            elif "retailer" in field_name:
                hierarchy["brand_type"] = "private_label"
                hierarchy["is_private_label"] = True
    
    return hierarchy

def validate_country_names(context_output: str) -> list:
    """
    Validate country names mentioned in brand context.
    
    Args:
        context_output: Raw brand context output
        
    Returns:
        list: List of validation warnings for country names
    """
    import re
    
    warnings = []
    
    # Common country name patterns
    valid_countries = [
        "usa", "united states", "america", "china", "japan", "germany", "italy", "france", 
        "uk", "united kingdom", "canada", "australia", "brazil", "india", "south korea",
        "mexico", "spain", "netherlands", "sweden", "norway", "denmark", "finland",
        "portugal", "switzerland", "austria", "belgium", "poland", "czech republic",
        "vietnam", "thailand", "malaysia", "indonesia", "philippines", "taiwan",
        "bangladesh", "pakistan", "turkey", "israel", "egypt", "south africa"
    ]
    
    # Extract potential country mentions
    country_pattern = r'country[^:]*:\s*([^,\n]+)'
    matches = re.findall(country_pattern, context_output.lower())
    
    for match in matches:
        country_name = match.strip()
        if country_name and country_name not in ["not specified", "not clearly specified"]:
            # Check if it's a recognized country
            if not any(valid_country in country_name for valid_country in valid_countries):
                warnings.append(f"Unusual country name detected: {country_name}")
    
    return warnings 