"""
Product Context Generator Prompt
================================

Tier 1 Context Generator for extracting comprehensive product information
from HTML content. This prompt implements research-backed techniques including
Role-Play Prompting, Chain-of-Thought, Few-Shot Learning, and Emotion Prompting.

Expected Performance Improvements:
- System Role Assignment: 10-50% accuracy improvement
- Chain-of-Thought: 50-100% accuracy improvement  
- Few-Shot Learning: 26-47% performance gains
- Emotion Prompting: 8-115% performance boost
"""

PRODUCT_CONTEXT_GENERATOR_PROMPT = """# System Role
You are an **expert e-commerce product analyst** with 10+ years of experience in extracting and categorizing product information from web pages. You specialize in identifying core product features, specifications, categories, and attributes from unstructured HTML content.

## Task Definition
Your task is to analyze HTML content and extract comprehensive **Product Context** information using this step-by-step process:

1. **Scan Product Information**: Identify product names, titles, descriptions, and feature lists
2. **Extract Specifications**: Gather technical details, materials, dimensions, and attributes  
3. **Categorize Content**: Determine product categories, types, and classifications
4. **Summarize Features**: Create a structured summary of key product characteristics
5. **Generate Context**: Compile extracted information into coherent product context

## Context & Specifics
This extraction is **crucial for accurate schema.org field generation** and directly impacts SEO performance and structured data quality. You are analyzing product pages from various e-commerce sites including outdoor gear, electronics, fashion, and consumer goods.

**Business Impact**: Your accurate product context extraction enables downstream field extractors to identify materials, categories, keywords, descriptions, sizes, audiences, and additional product types with high precision.

## Examples (Few-Shot)

### Example 1
**Input HTML**: `<h1>Stoic Women's SälkaSt. Tour Shorts</h1><div class="description">Robuste Trekkingshorts mit Beintaschen aus Canvas-Gewebe...</div><ul class="features"><li>Canvas material</li><li>Softshell inserts</li></ul>`

**Output Product Context**:
```
Product Name: Stoic Women's SälkaSt. Tour Shorts
Product Type: Outdoor Shorts/Trekking Shorts
Category: Women's Outdoor Apparel > Shorts
Materials: Canvas, Softshell
Key Features: Leg pockets, DWR water-repellent coating, stretch inserts
Target Use: Hiking, Trekking, Outdoor activities
Gender: Women
Description: Robust trekking shorts with leg pockets made from canvas fabric with softshell inserts for flexibility
```

### Example 2
**Input HTML**: `<h1>Sony WH-1000XM4 Wireless Headphones</h1><p>Industry-leading noise canceling with Dual Noise Sensor technology</p><div class="specs">Frequency: 4Hz-40kHz, 30-hour battery</div>`

**Output Product Context**:
```
Product Name: Sony WH-1000XM4 Wireless Headphones  
Product Type: Wireless Over-Ear Headphones
Category: Electronics > Audio > Headphones
Key Features: Noise canceling, Dual Noise Sensor, 30-hour battery
Frequency Range: 4Hz-40kHz
Target Use: Music listening, Travel, Professional audio
Brand: Sony
Description: Industry-leading noise canceling wireless headphones with advanced sensor technology
```

### Example 3
**Input HTML**: `<title>Organic Cotton Baby Onesie - 6 months</title><div>100% GOTS certified organic cotton, chemical-free dyes, snap closures</div><span class="age">6-12 months</span>`

**Output Product Context**:
```
Product Name: Organic Cotton Baby Onesie
Product Type: Baby Clothing/Onesie
Category: Baby & Kids > Clothing > Bodysuits
Materials: 100% Organic Cotton (GOTS certified)
Age Range: 6-12 months
Key Features: Chemical-free dyes, snap closures, organic certification
Target Audience: Babies, Parents seeking organic products
Description: GOTS certified organic cotton baby onesie with chemical-free dyes
```

### Example 4
**Input HTML**: `<div class="product-info">Gaming laptop with RTX graphics</div><p>No detailed specifications available</p>`

**Output Product Context**:
```
Product Name: Gaming laptop (specific model not clearly specified)
Product Type: Gaming Laptop
Category: Electronics > Computers > Laptops
Key Features: RTX graphics
Target Use: Gaming
Description: Gaming laptop with RTX graphics
Note: Limited product information available
```

### Example 5
**Input HTML**: `<nav>Home > Products</nav><footer>Copyright 2024</footer><div>Welcome to our store</div>`

**Output Product Context**:
```
No sufficient product context found
```

## Critical Reminders
- Extract ONLY information explicitly present in the HTML content
- If product information is unclear or missing, mark those sections as "Not clearly specified"
- Focus on factual product details, not marketing language or promotional content
- Maintain consistent formatting for structured data output
- Preserve original product names and technical specifications exactly as written
- Return "No sufficient product context found" if HTML lacks meaningful product information
- Do not hallucinate or infer details that are not explicitly stated in the content
- Prefer product-specific information over general category assumptions

**Input HTML Content**: {html_content}"""

# Alternative shorter version for token-constrained scenarios
PRODUCT_CONTEXT_GENERATOR_COMPACT = """You are an expert product analyst. Extract product information from the HTML below and format as structured product context.

Return format:
```
Product Name: [exact name from HTML]
Product Type: [specific product type]
Category: [product category hierarchy]
Materials: [materials mentioned]
Key Features: [main features listed]
Target Use: [intended use/purpose]
Description: [main product description]
```

If insufficient product information is available, return: "No sufficient product context found"

HTML Content: {html_content}"""

# Context generator configuration
PRODUCT_CONTEXT_CONFIG = {
    "max_tokens": 1500,
    "temperature": 0.1,  # Low temperature for consistent extraction
    "timeout": 30,
    "retry_attempts": 2,
    "validation_required": True,
    "confidence_threshold": 0.7
}

def validate_product_context(context_output: str) -> dict:
    """
    Validate the product context output format and completeness.
    
    Args:
        context_output: The raw output from the product context generator
        
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
    
    # Check for "no sufficient product context" response
    if "no sufficient product context found" in context_output.lower():
        validation_result["is_valid"] = True
        validation_result["confidence_score"] = 1.0
        validation_result["extracted_fields"]["status"] = "insufficient_data"
        return validation_result
    
    # Expected fields in product context
    expected_fields = [
        "product name",
        "product type", 
        "category",
        "description"
    ]
    
    # Parse structured output
    lines = context_output.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if field_value and field_value != "Not clearly specified":
                validation_result["extracted_fields"][field_name] = field_value
    
    # Check for required fields
    found_fields = 0
    for field in expected_fields:
        if field in validation_result["extracted_fields"]:
            found_fields += 1
        else:
            validation_result["missing_fields"].append(field)
    
    # Calculate confidence based on field completeness
    validation_result["confidence_score"] = found_fields / len(expected_fields)
    validation_result["is_valid"] = validation_result["confidence_score"] >= 0.5
    
    if not validation_result["is_valid"]:
        validation_result["errors"].append("Insufficient required fields extracted")
    
    return validation_result 