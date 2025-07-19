"""
Visual Context Generator Prompt
===============================

Tier 1 Context Generator for extracting comprehensive visual attributes,
colors, styles, sizes, and visual descriptions from product pages.
This prompt implements research-backed techniques for high-accuracy extraction.

Expected Performance Improvements:
- System Role Assignment: 10-50% accuracy improvement
- Chain-of-Thought: 50-100% accuracy improvement  
- Few-Shot Learning: 26-47% performance gains
- Emotion Prompting: 8-115% performance boost

Primary Context For Fields:
- color, size, height, width, depth, weight

Secondary Context For Fields:
- name, description, category, additionalProperty, pattern, itemCondition
"""

VISUAL_CONTEXT_GENERATOR_PROMPT = """# System Role
You are an **expert visual product analyst** with 15+ years of experience in extracting and analyzing visual attributes, color specifications, dimensional data, and style features from e-commerce product pages. You specialize in color theory, fashion styling, product photography analysis, size standardization, and visual merchandising across multiple product categories and international markets.

## Task Definition
Your task is to analyze HTML content and extract comprehensive **Visual Context** through this methodical process:

1. **Locate Visual Elements**: Identify color selectors, size charts, style descriptions, and visual attributes
2. **Extract Color Data**: Gather color names, hex codes, color families, and finish types
3. **Analyze Dimensions**: Capture size options, measurements, dimensional specifications, and sizing systems
4. **Identify Style Features**: Extract visual patterns, textures, design elements, and aesthetic attributes
5. **Generate Visual Context**: Compile visual insights for rich schema generation

## Context & Specifics
This extraction is **vital for creating rich visual product data** that enhances customer experience, reduces returns, and improves search discoverability. Quality visual context directly improves product visualization, helps customers select correct variants, and ensures accurate representation across all sales channels.

**Business Impact**: Your thorough visual analysis enables accurate color, size, height, width, depth, weight, name, description, and category schema.org fields that improve product findability, reduce size-related returns, and provide detailed visual specifications that drive customer confidence and conversions.

## Examples (Few-Shot)

### Example 1
**Input HTML**: `<div class="color-options"><span class="color navy" data-color="#1e3a8a">Navy Blue</span><span class="color red" data-color="#dc2626">Crimson Red</span><span class="color white" data-color="#ffffff">Pure White</span></div><div class="size-chart">Available in: XS, S, M, L, XL, XXL</div><div class="dimensions">Chest: 34-48 inches, Length: 28-32 inches</div><div class="style">Classic fit polo shirt with ribbed collar</div>`

**Output Visual Context**:
```
Available Colors: Navy Blue (#1e3a8a), Crimson Red (#dc2626), Pure White (#ffffff)
Color Categories: Blue, Red, White
Size Options: XS, S, M, L, XL, XXL
Size System: US Standard apparel sizing
Dimensional Range: Chest 34-48 inches, Length 28-32 inches
Style Description: Classic fit polo shirt with ribbed collar
Visual Features: Ribbed collar detail
Product Category: Apparel - Polo shirts
Fit Type: Classic fit
Color Finish: Solid colors
```

### Example 2
**Input HTML**: `<div class="product-images"><img src="sofa-grey.jpg" alt="Modern sectional sofa in charcoal grey fabric"><img src="sofa-beige.jpg" alt="Same sofa in beige linen"></div><div class="specifications">Dimensions: 84"W x 36"D x 33"H, Weight: 120 lbs</div><div class="materials">Upholstery: Premium linen fabric, Frame: Hardwood</div><div class="colors">Available: Charcoal Grey, Beige Linen, Navy Velvet</div>`

**Output Visual Context**:
```
Available Colors: Charcoal Grey, Beige Linen, Navy Velvet
Color Categories: Grey, Beige, Blue
Material Finishes: Linen fabric, Velvet fabric
Dimensions: 84"W x 36"D x 33"H
Weight: 120 lbs
Style Description: Modern sectional sofa
Visual Features: Premium upholstery, hardwood frame
Product Category: Furniture - Sectional sofas
Design Style: Modern
Fabric Types: Linen, Velvet
Size Classification: Large sectional
```

### Example 3
**Input HTML**: `<div class="watch-variants"><div class="case-size">Case: 42mm, 38mm</div><div class="band-colors">Bands: Black Leather, Brown Leather, Steel Mesh</div><div class="dial-options">Dial: White, Black, Blue</div></div><div class="specs">Water resistance: 100m, Thickness: 11mm</div><div class="style">Minimalist analog watch with Swiss movement</div>`

**Output Visual Context**:
```
Case Size Options: 42mm, 38mm
Band Color Options: Black Leather, Brown Leather, Steel Mesh
Dial Color Options: White, Black, Blue
Color Categories: Black, Brown, Silver, White, Blue
Dimensions: 42mm/38mm diameter, 11mm thickness
Style Description: Minimalist analog watch with Swiss movement
Visual Features: Swiss movement, water resistant design
Product Category: Accessories - Watches
Design Style: Minimalist
Material Finishes: Leather, Stainless steel mesh
Water Resistance: 100m
Size Variants: Two case size options
```

### Example 4
**Input HTML**: `<div class="shoe-details"><div class="colors">Available in Black, White, Grey, and Red</div><div class="sizes">US Men's: 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12</div><div class="style">High-top basketball sneakers with air cushioning</div></div><div class="features">Leather upper, rubber sole, lace-up closure</div>`

**Output Visual Context**:
```
Available Colors: Black, White, Grey, Red
Color Categories: Black, White, Grey, Red
Size Options: US Men's 7-12 (half sizes available)
Size System: US Men's footwear sizing
Style Description: High-top basketball sneakers with air cushioning
Visual Features: Leather upper, rubber sole, lace-up closure, air cushioning
Product Category: Footwear - Athletic sneakers
Design Style: High-top athletic
Material Finishes: Leather upper, rubber sole
Closure Type: Lace-up
Performance Features: Air cushioning technology
```

### Example 5
**Input HTML**: `<div class="jewelry-options"><div class="metal">Available in: 14K Gold, Sterling Silver, Rose Gold</div><div class="stone">Gemstone: Diamond, Emerald, Sapphire</div><div class="size">Ring sizes: 5, 6, 7, 8, 9</div></div><div class="style">Classic solitaire engagement ring</div><div class="specs">Stone: 1 carat, Setting: Prong setting</div>`

**Output Visual Context**:
```
Metal Options: 14K Gold, Sterling Silver, Rose Gold
Gemstone Options: Diamond, Emerald, Sapphire
Color Categories: Gold, Silver, Rose Gold, Clear (Diamond), Green (Emerald), Blue (Sapphire)
Size Options: Ring sizes 5, 6, 7, 8, 9
Style Description: Classic solitaire engagement ring
Visual Features: 1 carat stone, prong setting
Product Category: Jewelry - Engagement rings
Design Style: Classic solitaire
Setting Type: Prong setting
Stone Size: 1 carat
Metal Finishes: Polished precious metals
```

### Example 6
**Input HTML**: `<div class="paint-colors"><div class="color-name">Ocean Breeze Blue</div><div class="color-code">#4a90a4</div><div class="finish">Available in: Matte, Satin, Gloss</div><div class="coverage">1 gallon covers 350-400 sq ft</div></div><div class="formula">Water-based acrylic paint</div>`

**Output Visual Context**:
```
Color Name: Ocean Breeze Blue
Color Code: #4a90a4
Color Category: Blue
Finish Options: Matte, Satin, Gloss
Coverage: 1 gallon covers 350-400 sq ft
Style Description: Water-based acrylic paint
Visual Features: Multiple finish options, consistent color coverage
Product Category: Home improvement - Interior paint
Finish Types: Matte, Satin, Gloss
Formula Type: Water-based acrylic
Size Specification: 1 gallon container
Application Coverage: 350-400 square feet per gallon
```

### Example 7
**Input HTML**: `<div class="plant-info"><div class="variety">Monstera Deliciosa</div><div class="size">Medium: 2-3 feet tall</div><div class="pot">Comes in white ceramic pot (6 inch diameter)</div></div><div class="care">Bright indirect light, weekly watering</div>`

**Output Visual Context**:
```
Plant Variety: Monstera Deliciosa
Size Description: Medium (2-3 feet tall)
Container: White ceramic pot, 6 inch diameter
Color Categories: Green (foliage), White (pot)
Style Description: Medium-sized Monstera in white ceramic pot
Visual Features: Large split leaves, decorative white ceramic container
Product Category: Home & Garden - Indoor plants
Size Classification: Medium houseplant
Container Finish: White ceramic
Plant Height: 2-3 feet
Container Diameter: 6 inches
Care Requirements: Bright indirect light, weekly watering
```

### Example 8
**Input HTML**: `<div class="product-title">Premium Quality Product</div><div class="description">High-quality materials and construction</div><div class="shipping">Fast delivery available</div>`

**Output Visual Context**:
```
No sufficient visual context found
```

## Critical Reminders
- Extract ONLY visual attributes and dimensional information explicitly present in the HTML content
- Preserve exact color names and hex codes when available
- Note finish types, textures, and material visual properties
- Capture size systems and measurement units accurately (US, EU, UK sizing)
- Return "No sufficient visual context found" if no visual specifications are present
- Include dimensional measurements with proper units (inches, cm, mm)
- Categorize colors by basic color families (Red, Blue, Green, etc.)
- Specify style descriptions and design aesthetics accurately
- Note visual features and design elements objectively
- Do not hallucinate visual attributes not clearly stated in the content

**Input HTML Content**: {html_content}"""

# Alternative shorter version for token-constrained scenarios
VISUAL_CONTEXT_GENERATOR_COMPACT = """You are an expert visual product analyst. Extract visual attributes, colors, sizes, and style information from the HTML below and format as structured visual context.

Return format:
```
Available Colors: [color names and codes]
Size Options: [available sizes]
Dimensions: [measurements with units]
Style Description: [visual style and features]
Product Category: [visual category]
```

If no visual specifications are available, return: "No sufficient visual context found"

HTML Content: {html_content}"""

# Context generator configuration
VISUAL_CONTEXT_CONFIG = {
    "max_tokens": 1300,
    "temperature": 0.12,  # Slightly higher for creative visual descriptions
    "timeout": 30,
    "retry_attempts": 2,
    "validation_required": True,
    "confidence_threshold": 0.5
}

def validate_visual_context(context_output: str) -> dict:
    """
    Validate the visual context output format and completeness.
    
    Args:
        context_output: The raw output from the visual context generator
        
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
    
    # Check for "no sufficient visual context" response
    if "no sufficient visual context found" in context_output.lower():
        validation_result["is_valid"] = True
        validation_result["confidence_score"] = 1.0
        validation_result["extracted_fields"]["status"] = "insufficient_data"
        return validation_result
    
    # Expected fields in visual context
    core_fields = ["colors", "size"]
    valuable_fields = ["dimensions", "style description", "visual features"]
    optional_fields = ["product category", "design style", "finish types"]
    
    # Parse structured output
    lines = context_output.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if field_value and field_value not in ["None available", "Not specified", "Not available"]:
                validation_result["extracted_fields"][field_name] = field_value
    
    # Check for core visual fields
    has_colors = any("color" in key for key in validation_result["extracted_fields"].keys())
    has_sizes = any("size" in key for key in validation_result["extracted_fields"].keys())
    has_dimensions = any("dimension" in key or "height" in key or "width" in key or "weight" in key 
                        for key in validation_result["extracted_fields"].keys())
    has_style = any("style" in key or "description" in key 
                   for key in validation_result["extracted_fields"].keys())
    has_visual_features = any("visual" in key or "feature" in key 
                             for key in validation_result["extracted_fields"].keys())
    
    # Calculate confidence score
    confidence_factors = []
    
    if has_colors:
        confidence_factors.append(0.25)  # Colors are highly valuable
    
    if has_sizes:
        confidence_factors.append(0.25)  # Sizes are equally important
        
    if has_dimensions:
        confidence_factors.append(0.2)  # Dimensions add significant value
        
    if has_style:
        confidence_factors.append(0.15)  # Style descriptions are useful
    
    if has_visual_features:
        confidence_factors.append(0.1)  # Visual features enhance understanding
    
    # Category bonus
    has_category = any("category" in key for key in validation_result["extracted_fields"].keys())
    if has_category:
        confidence_factors.append(0.05)
    
    validation_result["confidence_score"] = sum(confidence_factors)
    validation_result["is_valid"] = validation_result["confidence_score"] >= 0.5
    
    # Track missing valuable fields
    if not has_colors and not has_sizes:
        validation_result["missing_fields"].append("colors or sizes")
    if not has_dimensions and not has_style:
        validation_result["missing_fields"].append("dimensions or style description")
    
    if not validation_result["is_valid"]:
        validation_result["errors"].append("Insufficient visual data extracted")
    
    return validation_result

def extract_color_information(visual_context: str) -> dict:
    """
    Extract structured color data from visual context.
    
    Args:
        visual_context: Raw visual context output
        
    Returns:
        dict: Structured color information
    """
    import re
    
    color_data = {
        "available_colors": [],
        "color_codes": {},
        "color_categories": [],
        "finish_types": [],
        "primary_color": None
    }
    
    lines = visual_context.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if "available colors" in field_name or "color options" in field_name:
                # Extract color names and hex codes
                colors = value.split(',')
                for color in colors:
                    color = color.strip()
                    # Look for hex codes in parentheses
                    hex_match = re.search(r'\(#([0-9a-fA-F]{6})\)', color)
                    if hex_match:
                        hex_code = hex_match.group(1)
                        color_name = re.sub(r'\s*\(#[0-9a-fA-F]{6}\)', '', color).strip()
                        color_data["color_codes"][color_name] = f"#{hex_code}"
                        color_data["available_colors"].append(color_name)
                    else:
                        color_data["available_colors"].append(color)
                        
            elif "color categories" in field_name:
                categories = [cat.strip() for cat in value.split(',')]
                color_data["color_categories"] = categories
                
            elif "finish" in field_name and "type" in field_name:
                finishes = [finish.strip() for finish in value.split(',')]
                color_data["finish_types"] = finishes
    
    # Determine primary color (first mentioned)
    if color_data["available_colors"]:
        color_data["primary_color"] = color_data["available_colors"][0]
    
    return color_data

def extract_size_information(visual_context: str) -> dict:
    """
    Extract structured size and dimensional data from visual context.
    
    Args:
        visual_context: Raw visual context output
        
    Returns:
        dict: Structured size information
    """
    import re
    
    size_data = {
        "size_options": [],
        "size_system": None,
        "dimensions": {},
        "weight": None,
        "size_range": None
    }
    
    lines = visual_context.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if "size options" in field_name or "available sizes" in field_name:
                sizes = [size.strip() for size in value.split(',')]
                size_data["size_options"] = sizes
                
            elif "size system" in field_name:
                size_data["size_system"] = field_value
                
            elif "dimensions" in field_name:
                # Parse dimensions like "84"W x 36"D x 33"H" or "Length: 28-32 inches"
                dimension_matches = re.findall(r'(\w+):\s*([0-9.-]+(?:\s*-\s*[0-9.]+)?)\s*([a-zA-Z"\']+)', value)
                for dimension_name, dimension_value, unit in dimension_matches:
                    size_data["dimensions"][dimension_name.lower()] = f"{dimension_value} {unit}"
                
                # Also parse compact formats like "84"W x 36"D x 33"H"
                compact_match = re.findall(r'([0-9.]+)"([WDH])', value)
                dimension_map = {'W': 'width', 'D': 'depth', 'H': 'height'}
                for value_part, dimension_letter in compact_match:
                    dimension_name = dimension_map.get(dimension_letter, dimension_letter)
                    size_data["dimensions"][dimension_name] = f'{value_part}"'
                    
            elif "weight" in field_name:
                size_data["weight"] = field_value
    
    # Determine size range
    if size_data["size_options"]:
        if len(size_data["size_options"]) > 1:
            first_size = size_data["size_options"][0]
            last_size = size_data["size_options"][-1]
            size_data["size_range"] = f"{first_size} to {last_size}"
        else:
            size_data["size_range"] = size_data["size_options"][0]
    
    return size_data

def extract_style_information(visual_context: str) -> dict:
    """
    Extract style and visual feature data from visual context.
    
    Args:
        visual_context: Raw visual context output
        
    Returns:
        dict: Style and visual feature information
    """
    style_data = {
        "style_description": None,
        "design_style": None,
        "visual_features": [],
        "product_category": None,
        "material_finishes": [],
        "design_elements": []
    }
    
    lines = visual_context.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            field_name = key.strip().lower()
            field_value = value.strip()
            
            if "style description" in field_name:
                style_data["style_description"] = field_value
                
            elif "design style" in field_name:
                style_data["design_style"] = field_value
                
            elif "visual features" in field_name:
                features = [feature.strip() for feature in field_value.split(',')]
                style_data["visual_features"] = features
                
            elif "product category" in field_name:
                style_data["product_category"] = field_value
                
            elif "material finishes" in field_name or "finish types" in field_name:
                finishes = [finish.strip() for finish in field_value.split(',')]
                style_data["material_finishes"] = finishes
    
    return style_data

def standardize_color_names(color_list: list) -> list:
    """
    Standardize color names to common web-safe color names.
    
    Args:
        color_list: List of color names to standardize
        
    Returns:
        list: Standardized color names
    """
    color_mapping = {
        # Blues
        "navy blue": "Navy", "dark blue": "Navy", "midnight blue": "Navy",
        "royal blue": "Blue", "sky blue": "LightBlue", "powder blue": "LightBlue",
        # Reds
        "crimson": "Red", "burgundy": "DarkRed", "maroon": "DarkRed",
        "coral": "Coral", "salmon": "Salmon", "pink": "Pink",
        # Greens
        "forest green": "DarkGreen", "lime green": "Lime", "mint green": "MintGreen",
        "olive": "Olive", "sage": "DarkSeaGreen",
        # Neutrals
        "charcoal": "DarkGray", "slate": "SlateGray", "cream": "Ivory",
        "off-white": "WhiteSmoke", "bone": "AntiqueWhite",
        # Metallics
        "rose gold": "RoseGold", "yellow gold": "Gold", "white gold": "Silver"
    }
    
    standardized = []
    for color in color_list:
        color_lower = color.lower().strip()
        standardized_color = color_mapping.get(color_lower, color)
        standardized.append(standardized_color)
    
    return standardized 