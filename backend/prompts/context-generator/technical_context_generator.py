"""
Technical Context Generator Prompt
==================================

Tier 1 Context Generator for extracting comprehensive technical specifications,
materials, manufacturing details, compliance data, and product identifiers.
This prompt implements research-backed techniques for high-accuracy extraction.

Expected Performance Improvements:
- System Role Assignment: 10-50% accuracy improvement
- Chain-of-Thought: 50-100% accuracy improvement  
- Few-Shot Learning: 26-47% performance gains
- Emotion Prompting: 8-115% performance boost

Primary Context For Fields:
- material, nsn, countryOfLastProcessing

Secondary Context For Fields:
- mpn, gtin, productID, model, itemCondition, category, additionalProperty
"""

TECHNICAL_CONTEXT_GENERATOR_PROMPT = """# System Role
You are an **expert technical product analyst** with 20+ years of experience in extracting and analyzing technical specifications, materials, manufacturing data, and compliance information from product documentation. You specialize in engineering specifications, material science, manufacturing processes, quality standards, and regulatory compliance across multiple industries and international markets.

## Task Definition
Your task is to analyze HTML content and extract comprehensive **Technical Context** through this methodical process:

1. **Locate Technical Sections**: Identify specification tables, material lists, technical documentation, and compliance data
2. **Extract Material Data**: Gather material composition, construction details, and manufacturing information
3. **Analyze Specifications**: Capture technical measurements, performance data, and engineering specifications
4. **Identify Compliance**: Extract certifications, standards, country of origin, and regulatory information
5. **Generate Tech Context**: Compile technical insights for precise schema generation

## Context & Specifics
This extraction is **critical for creating accurate technical product data** that ensures regulatory compliance, enables proper categorization, and provides essential specification details. Quality technical context directly improves search accuracy, helps customers find compatible products, and ensures compliance with international trade and safety regulations.

**Business Impact**: Your thorough technical analysis enables accurate material, nsn, countryOfLastProcessing, mpn, gtin, productID, and model schema.org fields that improve product discoverability, ensure regulatory compliance, and provide essential technical details that drive informed purchasing decisions.

## Examples (Few-Shot)

### Example 1
**Input HTML**: `<div class="materials">100% Organic Cotton</div><div class="specs">Weight: 180gsm, Country of Origin: Turkey</div><div class="certifications">GOTS Certified, Oeko-Tex Standard 100</div><div class="product-codes">SKU: TCG-001, UPC: 123456789012</div><div class="manufacturing">Last Processed: Turkey, Mill: Denizli Textile</div>`

**Output Technical Context**:
```
Materials: 100% Organic Cotton
Weight Specification: 180gsm
Country of Origin: Turkey
Country of Last Processing: Turkey
Manufacturing Location: Denizli Textile mill
Certifications: GOTS Certified, Oeko-Tex Standard 100
Product Codes: SKU: TCG-001, UPC: 123456789012
Quality Standards: Organic certification, textile safety standard
Material Category: Natural fiber, organic textile
Technical Specifications: Weight density 180 grams per square meter
```

### Example 2
**Input HTML**: `<table class="tech-specs"><tr><td>Material</td><td>316 Stainless Steel</td></tr><tr><td>Dimensions</td><td>15cm x 8cm x 3cm</td></tr><tr><td>Weight</td><td>450g</td></tr><tr><td>Finish</td><td>Brushed stainless steel</td></tr></table><div class="origin">Made in Germany</div><div class="standards">FDA Approved, NSF Certified</div><div class="model">Model: KT-450-SS</div>`

**Output Technical Context**:
```
Materials: 316 Stainless Steel
Dimensions: 15cm x 8cm x 3cm
Weight: 450g
Surface Finish: Brushed stainless steel
Country of Origin: Germany
Country of Last Processing: Germany
Model Number: KT-450-SS
Certifications: FDA Approved, NSF Certified
Material Grade: 316 stainless steel (food grade)
Technical Category: Kitchen utensil, stainless steel cookware
Quality Standards: FDA food safety, NSF sanitation standard
```

### Example 3
**Input HTML**: `<div class="components">Aluminum frame, Polycarbonate lens, Silicone nose pads</div><div class="specs">UV400 Protection, Anti-reflective coating</div><div class="compliance">CE Marked, ANSI Z87.1 Compliant</div><div class="origin">Designed in USA, Manufactured in China</div><div class="condition">New - Factory sealed</div><div class="identifiers">UPC: 987654321098, MPN: SG-UV400-BLK</div>`

**Output Technical Context**:
```
Materials: Aluminum frame, Polycarbonate lens, Silicone nose pads
Protective Features: UV400 Protection, Anti-reflective coating
Country of Origin: China
Country of Last Processing: China
Design Origin: USA
Item Condition: New - Factory sealed
Product Identifiers: UPC: 987654321098, MPN: SG-UV400-BLK
Compliance Standards: CE Marked, ANSI Z87.1 Compliant
Material Components: Metal frame, plastic lens, rubber contact points
Safety Category: Eye protection, UV filtering eyewear
Technical Specifications: UV400 protection standard, impact resistance
```

### Example 4
**Input HTML**: `<div class="fabric-content">65% Polyester, 35% Cotton blend</div><div class="care">Machine washable, Tumble dry low</div><div class="sizing">Pre-shrunk, True to size</div><div class="country">Made in Bangladesh</div><div class="tags">Style: 4XL-REG, Color: Navy Blue</div><div class="barcode">EAN: 1234567890123</div>`

**Output Technical Context**:
```
Materials: 65% Polyester, 35% Cotton blend
Care Instructions: Machine washable, Tumble dry low
Country of Origin: Bangladesh
Country of Last Processing: Bangladesh
Pre-treatment: Pre-shrunk
Item Condition: New
Product Identifiers: EAN: 1234567890123
Style Specifications: 4XL-REG size, Navy Blue color
Material Category: Poly-cotton blend textile
Technical Features: Pre-shrunk treatment, size-stable
Quality Attributes: Machine washable, low-heat drying
```

### Example 5
**Input HTML**: `<div class="electronics-specs">Lithium-ion battery, 5000mAh capacity</div><div class="compliance">FCC ID: ABC123XYZ, IC: 456-DEF789</div><div class="ratings">Input: 5V/2A, Output: 5V/2.4A</div><div class="safety">UL Listed, RoHS Compliant</div><div class="manufacturing">Assembled in Vietnam, Components from South Korea</div><div class="model">Model: PB-5000-USB</div>`

**Output Technical Context**:
```
Materials: Lithium-ion battery technology
Battery Capacity: 5000mAh
Electrical Specifications: Input: 5V/2A, Output: 5V/2.4A
Country of Origin: Vietnam
Country of Last Processing: Vietnam
Component Origin: South Korea
Model Number: PB-5000-USB
Regulatory Compliance: FCC ID: ABC123XYZ, IC: 456-DEF789
Safety Certifications: UL Listed, RoHS Compliant
Technical Category: Portable power bank, electronic device
Quality Standards: UL safety standard, RoHS environmental compliance
Manufacturing Process: Assembly in Vietnam with Korean components
```

### Example 6
**Input HTML**: `<div class="product-info">Handcrafted wooden toy</div><div class="wood-type">Sustainable beech wood</div><div class="finish">Non-toxic water-based paint</div><div class="age">3+ years</div><div class="origin">Handmade in Poland</div><div class="safety">EN71 Certified, CPSIA Compliant</div>`

**Output Technical Context**:
```
Materials: Sustainable beech wood
Surface Treatment: Non-toxic water-based paint
Country of Origin: Poland
Country of Last Processing: Poland
Manufacturing Method: Handcrafted
Item Condition: New
Age Suitability: 3+ years
Safety Certifications: EN71 Certified, CPSIA Compliant
Material Category: Natural wood, sustainable forestry
Quality Standards: European toy safety (EN71), US toy safety (CPSIA)
Technical Features: Non-toxic finish, child-safe materials
Sustainability: Sustainable wood sourcing
```

### Example 7
**Input HTML**: `<div class="vintage-info">Original 1970s design</div><div class="condition">Used - Good condition, minor wear</div><div class="materials">Brass and glass construction</div><div class="restoration">Recently restored, new wiring</div><div class="origin">Made in West Germany</div>`

**Output Technical Context**:
```
Materials: Brass and glass construction
Country of Origin: West Germany
Country of Last Processing: West Germany (historical)
Item Condition: Used - Good condition, minor wear
Manufacturing Era: 1970s original design
Restoration Status: Recently restored, new wiring
Technical Category: Vintage lighting, brass fixture
Historical Context: West German manufacturing
Quality Assessment: Good condition with minor wear, professionally restored
Technical Updates: New electrical wiring installed
```

### Example 8
**Input HTML**: `<div class="product-details">Product information available</div><div class="shipping">Standard delivery options</div><div class="warranty">1-year manufacturer warranty</div>`

**Output Technical Context**:
```
No sufficient technical context found
```

## Critical Reminders
- Extract ONLY technical specifications and material information explicitly present in the HTML content
- Distinguish between country of origin and country of last processing when both are mentioned
- Preserve exact material compositions and technical measurements
- Note certifications, compliance standards, and regulatory information accurately
- Return "No sufficient technical context found" if no technical specifications are present
- Include product identifiers (UPC, EAN, MPN, SKU) when available
- Categorize materials by type (natural, synthetic, composite, etc.)
- Specify item condition accurately (new, used, refurbished, etc.)
- Note manufacturing methods (handcrafted, machine-made, assembled)
- Do not hallucinate technical specifications not clearly stated in the content

**Input HTML Content**: {html_content}"""

# Alternative shorter version for token-constrained scenarios
TECHNICAL_CONTEXT_GENERATOR_COMPACT = """You are an expert technical product analyst. Extract technical specifications, materials, and manufacturing information from the HTML below and format as structured technical context.

Return format:
```
Materials: [material composition]
Country of Origin: [manufacturing country]
Technical Specifications: [key specs and measurements]
Product Identifiers: [UPC, MPN, SKU etc.]
Item Condition: [new/used/refurbished]
```

If no technical specifications are available, return: "No sufficient technical context found"

HTML Content: {html_content}"""

# Context generator configuration
TECHNICAL_CONTEXT_CONFIG = {
    "max_tokens": 1200,
    "temperature": 0.1,  # Very low for precise technical extraction
    "timeout": 30,
    "retry_attempts": 2,
    "validation_required": True,
    "confidence_threshold": 0.5
}

def validate_technical_context(context_output: str) -> dict:
    """
    Validate the technical context output format and completeness.
    
    Args:
        context_output: The raw output from the technical context generator
        
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
    
    # Check for "no sufficient technical context" response
    if "no sufficient technical context found" in context_output.lower():
        validation_result["is_valid"] = True
        validation_result["confidence_score"] = 1.0
        validation_result["extracted_fields"]["status"] = "insufficient_data"
        return validation_result
    
    # Expected fields in technical context
    core_fields = ["materials", "country of origin"]
    valuable_fields = ["technical specifications", "product identifiers", "item condition"]
    optional_fields = ["certifications", "model number", "manufacturing method"]
    
    # Parse structured output
    lines = context_output.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if field_value and field_value not in ["None available", "Not specified", "Not available"]:
                validation_result["extracted_fields"][field_name] = field_value
    
    # Check for core technical fields
    has_materials = any("material" in key for key in validation_result["extracted_fields"].keys())
    has_origin = any("origin" in key or "country" in key for key in validation_result["extracted_fields"].keys())
    has_specs = any("specification" in key or "dimension" in key or "weight" in key 
                   for key in validation_result["extracted_fields"].keys())
    has_identifiers = any("identifier" in key or "upc" in key or "mpn" in key or "sku" in key 
                         for key in validation_result["extracted_fields"].keys())
    has_condition = any("condition" in key for key in validation_result["extracted_fields"].keys())
    
    # Calculate confidence score
    confidence_factors = []
    
    if has_materials:
        confidence_factors.append(0.3)  # Materials are most important
    
    if has_origin:
        confidence_factors.append(0.2)  # Origin is valuable for compliance
        
    if has_specs:
        confidence_factors.append(0.2)  # Technical specs add value
        
    if has_identifiers:
        confidence_factors.append(0.15)  # Product IDs are useful
    
    if has_condition:
        confidence_factors.append(0.1)  # Condition is helpful
    
    # Certifications bonus
    has_certifications = any("certification" in key or "compliance" in key 
                           for key in validation_result["extracted_fields"].keys())
    if has_certifications:
        confidence_factors.append(0.05)
    
    validation_result["confidence_score"] = sum(confidence_factors)
    validation_result["is_valid"] = validation_result["confidence_score"] >= 0.5
    
    # Track missing valuable fields
    if not has_materials:
        validation_result["missing_fields"].append("materials")
    if not has_origin:
        validation_result["missing_fields"].append("country of origin")
    if not has_specs and not has_identifiers:
        validation_result["missing_fields"].append("technical specifications or identifiers")
    
    if not validation_result["is_valid"]:
        validation_result["errors"].append("Insufficient technical data extracted")
    
    return validation_result

def extract_material_composition(technical_context: str) -> dict:
    """
    Extract structured material composition data from technical context.
    
    Args:
        technical_context: Raw technical context output
        
    Returns:
        dict: Structured material information
    """
    import re
    
    material_data = {
        "primary_material": None,
        "material_percentage": {},
        "material_type": None,
        "material_grade": None,
        "sustainability": None
    }
    
    # Extract percentage-based compositions
    percentage_pattern = r'(\d+)%\s*([^,\n]+)'
    percentage_matches = re.findall(percentage_pattern, technical_context)
    
    for percentage, material in percentage_matches:
        material_name = material.strip()
        material_data["material_percentage"][material_name] = int(percentage)
    
    # Find primary material (highest percentage or first mentioned)
    if material_data["material_percentage"]:
        primary = max(material_data["material_percentage"].items(), key=lambda x: x[1])
        material_data["primary_material"] = primary[0]
    
    # Extract material type keywords
    material_types = {
        "natural": ["cotton", "wool", "silk", "linen", "leather", "wood", "bamboo"],
        "synthetic": ["polyester", "nylon", "acrylic", "plastic", "vinyl"],
        "metal": ["steel", "aluminum", "brass", "copper", "iron", "titanium"],
        "composite": ["blend", "composite", "laminate", "plywood"]
    }
    
    context_lower = technical_context.lower()
    for material_type, keywords in material_types.items():
        if any(keyword in context_lower for keyword in keywords):
            material_data["material_type"] = material_type
            break
    
    # Extract sustainability indicators
    sustainability_keywords = ["organic", "sustainable", "recycled", "eco-friendly", "gots", "fair trade"]
    if any(keyword in context_lower for keyword in sustainability_keywords):
        material_data["sustainability"] = "sustainable_certified"
    
    # Extract material grades (for metals, plastics)
    grade_pattern = r'(\d+)\s*(stainless steel|grade|series)'
    grade_match = re.search(grade_pattern, context_lower)
    if grade_match:
        material_data["material_grade"] = grade_match.group(0)
    
    return material_data

def extract_country_information(technical_context: str) -> dict:
    """
    Extract country of origin and manufacturing information.
    
    Args:
        technical_context: Raw technical context output
        
    Returns:
        dict: Country and manufacturing data
    """
    import re
    
    country_data = {
        "country_of_origin": None,
        "country_of_last_processing": None,
        "manufacturing_method": None,
        "assembly_location": None
    }
    
    lines = technical_context.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if "country of origin" in field_name:
                country_data["country_of_origin"] = field_value
            elif "country of last processing" in field_name:
                country_data["country_of_last_processing"] = field_value
            elif "manufacturing method" in field_name or "manufacturing process" in field_name:
                country_data["manufacturing_method"] = field_value
            elif "assembled" in field_name or "assembly" in field_name:
                country_data["assembly_location"] = field_value
    
    # Extract manufacturing methods
    method_patterns = [
        r'handcrafted|handmade|hand-made',
        r'machine made|machine-made|manufactured',
        r'assembled|assembly',
        r'forged|cast|molded|printed'
    ]
    
    context_lower = technical_context.lower()
    for pattern in method_patterns:
        match = re.search(pattern, context_lower)
        if match and not country_data["manufacturing_method"]:
            country_data["manufacturing_method"] = match.group(0)
            break
    
    return country_data

def extract_product_identifiers(technical_context: str) -> dict:
    """
    Extract product codes and identifiers from technical context.
    
    Args:
        technical_context: Raw technical context output
        
    Returns:
        dict: Product identifier data
    """
    import re
    
    identifier_data = {
        "upc": None,
        "ean": None,
        "mpn": None,
        "sku": None,
        "model": None,
        "gtin": None
    }
    
    # Define patterns for different identifier types
    patterns = {
        "upc": r'upc:?\s*([0-9]{12})',
        "ean": r'ean:?\s*([0-9]{13})',
        "mpn": r'mpn:?\s*([a-zA-Z0-9\-]+)',
        "sku": r'sku:?\s*([a-zA-Z0-9\-]+)',
        "model": r'model:?\s*([a-zA-Z0-9\-\s]+)',
        "gtin": r'gtin:?\s*([0-9]{8,14})'
    }
    
    context_lower = technical_context.lower()
    
    for identifier_type, pattern in patterns.items():
        match = re.search(pattern, context_lower)
        if match:
            identifier_data[identifier_type] = match.group(1).strip()
    
    # Handle model numbers from "Model:" lines
    lines = technical_context.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if "model" in field_name and not identifier_data["model"]:
                identifier_data["model"] = field_value
    
    return identifier_data 