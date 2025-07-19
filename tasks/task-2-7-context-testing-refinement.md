# Task 2.7: Context Generator Testing & Refinement

## Overview

Comprehensive testing and refinement of all 6 context generators against `/data/rich-schema.json` examples to ensure optimal coverage, accuracy, and token efficiency for schema.org Product field extraction.

## Testing Framework

### 1. Validation Dataset Analysis

**Rich Schema Target**: `/data/rich-schema.json`

- **Product Type**: Women's Trekking Shorts (Stoic brand)
- **Complexity**: ProductGroup with multiple variants by color/size
- **Fields Present**: 23 out of 23 target fields covered
- **Multilingual**: German descriptions with technical details

**Shallow Schema Starting Point**: `/data/shallow-schema.json`

- **Basic Fields**: @type, sku, gtin, name, description, offers (URL, currency, price)
- **Missing Fields**: 18 critical fields need enrichment
- **Enrichment Gap**: 78% of target fields require context generation

### 2. Context Generator Coverage Matrix

| Context Generator      | Primary Fields                    | Secondary Fields             | Token Budget | Rich Schema Match                              |
| ---------------------- | --------------------------------- | ---------------------------- | ------------ | ---------------------------------------------- |
| **Product Context**    | name, description, category       | brand, audience              | 1200         | ✅ Brand extraction, category classification   |
| **Commercial Context** | offers, price, availability       | seller, warranty             | 1100         | ✅ Pricing, availability, shipping integration |
| **Brand Context**      | brand, manufacturer               | countryOfOrigin              | 1000         | ✅ "Stoic" brand identification                |
| **UX Context**         | aggregateRating, review           | positiveNotes, negativeNotes | 1400         | ⚠️ No review data in test case                 |
| **Technical Context**  | material, countryOfLastProcessing | mpn, itemCondition           | 1200         | ⚠️ Limited technical specs in name/description |
| **Visual Context**     | color, size, dimensions           | pattern, style               | 1300         | ✅ Color/size extraction from variants         |

**Total Token Budget**: 7,200 tokens across all generators

### 3. Rich Schema Field Coverage Testing

**Target Fields Analysis** (from rich-schema.json):

```json
{
  "Critical Fields Present": {
    "name": "Stoic - Women's SälkaSt. Tour Shorts - Shorts - Black | 34 (EU)",
    "description": "Robuste Trekkingshorts mit Beintaschen...",
    "brand": {"@type": "Brand", "name": "Stoic"},
    "color": "Black", "Forest Green",
    "size": "34", "36", "38", "40", "42", "44", "46",
    "sku": "112-2189-0111",
    "gtin": "5714855001666",
    "offers": {"price": 29.99, "priceCurrency": "EUR", "availability": "InStock/OutOfStock"},
    "audience": {"suggestedGender": "women"},
    "itemCondition": "NewCondition",
    "image": "product images with variants"
  },

  "Missing in Test Case": {
    "aggregateRating": "No review data",
    "review": "No customer feedback",
    "material": "Technical specs in description only",
    "countryOfOrigin": "Not specified in test data",
    "weight/dimensions": "Not in current schema"
  }
}
```

### 4. Context Generator Performance Tests

#### Test Case 1: Product Context Generator

**Input HTML Simulation**:

```html
<h1>Stoic - Women's SälkaSt. Tour Shorts - Shorts</h1>
<div class="description">
  Robuste Trekkingshorts mit Beintaschen Die Women's SälkaSt.Tour Shorts von
  Stoic besteht aus einem äußerst robusten und abriebfesten Canvas-Gewebe...
</div>
<div class="brand">Stoic</div>
<div class="category">Shorts > Women's Apparel > Outdoor Clothing</div>
```

**Expected Output**:

```
Product Name: Stoic - Women's SälkaSt. Tour Shorts - Shorts
Brand: Stoic
Product Category: Women's Outdoor Shorts
Description: Robuste Trekkingshorts mit Beintaschen - robust trekking shorts with leg pockets
Target Audience: Women
Activity Category: Trekking, Hiking, Outdoor Activities
Product Type: Outdoor apparel, technical clothing
```

**Validation Criteria**:

- ✅ Brand extraction accuracy: "Stoic" identified correctly
- ✅ Category classification: "Women's Outdoor Shorts" vs raw "Shorts"
- ✅ Audience identification: "Women" from product name
- ✅ Activity context: "Trekking, Hiking" from German description

#### Test Case 2: Visual Context Generator

**Input HTML Simulation**:

```html
<div class="color-variants">
  <span class="color-option" data-color="Black">Black</span>
  <span class="color-option" data-color="Forest Green">Forest Green</span>
</div>
<div class="size-options">
  34 (EU), 36 (EU), 38 (EU), 40 (EU), 42 (EU), 44 (EU), 46 (EU)
</div>
<div class="product-images">
  <img src="sol_112-2189-0111_pic1_1.jpg" alt="Black shorts" />
  <img src="sol_112-2189-0211_pic1_1.jpg" alt="Forest Green shorts" />
</div>
```

**Expected Output**:

```
Available Colors: Black, Forest Green
Color Categories: Black, Green
Size Options: 34 (EU), 36 (EU), 38 (EU), 40 (EU), 42 (EU), 44 (EU), 46 (EU)
Size System: EU Women's apparel sizing
Style Description: Women's outdoor trekking shorts
Product Category: Apparel - Women's Shorts
Size Range: EU 34 to 46
```

**Validation Criteria**:

- ✅ Color extraction: Both "Black" and "Forest Green" identified
- ✅ Size system recognition: "EU" sizing system identified
- ✅ Size range processing: Full range 34-46 captured
- ✅ Style categorization: "Women's outdoor trekking shorts"

#### Test Case 3: Technical Context Generator

**Input HTML Simulation**:

```html
<div class="materials">Canvas-Gewebe, Softshell-Einsätze</div>
<div class="features">PFC-freie DWR-Imprägnierung, Atmungsaktiv, Stretch</div>
<div class="specifications">
  <span>SKU: 112-2189-0111</span>
  <span>GTIN: 5714855001666</span>
</div>
<div class="condition">New</div>
```

**Expected Output**:

```
Materials: Canvas fabric, Softshell inserts
Technical Features: PFC-free DWR coating, Breathable, Stretch panels
Product Identifiers: SKU: 112-2189-0111, GTIN: 5714855001666
Item Condition: New
Material Category: Technical outdoor fabric
Performance Features: Water-resistant, breathable, flexible construction
```

**Validation Criteria**:

- ✅ Material extraction: "Canvas" and "Softshell" identified
- ✅ Technical features: DWR coating, breathability captured
- ✅ Product codes: SKU and GTIN accurately extracted
- ⚠️ Country of origin: Not available in test case

### 5. Token Efficiency Optimization

**Current Token Distribution**:

```
Product Context:     1200 tokens (16.7%)
Commercial Context:  1100 tokens (15.3%)
Brand Context:       1000 tokens (13.9%)
UX Context:          1400 tokens (19.4%)
Technical Context:   1200 tokens (16.7%)
Visual Context:      1300 tokens (18.1%)
─────────────────────────────────────
Total Budget:        7200 tokens (100%)
```

**Optimization Strategies**:

1. **Dynamic Context Selection**:

   - Skip UX Context when no reviews present (saves 1400 tokens)
   - Use compact versions for simple products (30-50% reduction)
   - Prioritize contexts with highest field coverage

2. **Token-Efficient Examples**:

   - Reduce from 7-8 examples to 4-5 core examples per generator
   - Focus on most common product scenarios
   - Eliminate redundant examples

3. **Compact Template Usage**:
   ```python
   # Use compact version when token budget is constrained
   if total_tokens > budget_limit:
       return CONTEXT_GENERATOR_COMPACT.format(html_content=html)
   else:
       return CONTEXT_GENERATOR_PROMPT.format(html_content=html)
   ```

### 6. Coverage Gap Analysis

**Field Coverage by Context Type**:

| Field Category        | Coverage Status | Generator        | Confidence |
| --------------------- | --------------- | ---------------- | ---------- |
| **Product Identity**  | ✅ Complete     | Product + Visual | High       |
| **Brand Information** | ✅ Complete     | Brand + Product  | High       |
| **Pricing & Offers**  | ✅ Complete     | Commercial       | High       |
| **Visual Attributes** | ✅ Complete     | Visual           | High       |
| **Technical Specs**   | ⚠️ Partial      | Technical        | Medium     |
| **User Experience**   | ❌ Missing      | UX (no data)     | Low        |
| **Manufacturing**     | ❌ Missing      | Technical        | Low        |

**Recommended Improvements**:

1. **Technical Context Enhancement**:

   - Add material extraction from German descriptions
   - Improve country of origin inference
   - Enhanced technical feature parsing

2. **UX Context Adaptation**:

   - Handle "no reviews" scenarios gracefully
   - Extract review prompts/placeholders
   - Focus on available customer signals

3. **Cross-Generator Intelligence**:
   - Share brand context across generators
   - Visual context informs technical specs
   - Product context enhances commercial data

### 7. Real-World Testing Scenarios

**Test Scenario A: Complete Product Page**

- Rich HTML with all context types present
- Expected: 90%+ field coverage with all 6 generators

**Test Scenario B: Minimal Product Page**

- Basic product info only (like shallow-schema.json)
- Expected: 60%+ field coverage with 3-4 relevant generators

**Test Scenario C: Product Variants**

- Multiple colors/sizes like rich-schema.json
- Expected: Complete variant extraction with proper grouping

**Test Scenario D: Non-English Content**

- German descriptions like test case
- Expected: Accurate extraction despite language barriers

### 8. Validation Metrics

**Accuracy Metrics**:

- **Field Extraction Accuracy**: 95%+ for present fields
- **Context Relevance Score**: 85%+ confidence on generated context
- **Schema Completeness**: 80%+ of target fields populated

**Efficiency Metrics**:

- **Token Utilization**: <7200 tokens total across all generators
- **Processing Time**: <60 seconds for complete extraction
- **Coverage Ratio**: Fields extracted / Fields available in HTML

**Quality Metrics**:

- **Brand Recognition**: 98%+ accuracy on brand extraction
- **Color/Size Parsing**: 95%+ accuracy on variant data
- **Price/Availability**: 100% accuracy on structured data

### 9. Refinement Recommendations

**Immediate Optimizations**:

1. **Example Reduction**: Cut examples from 7-8 to 4-5 per generator (-20% tokens)
2. **Compact Versions**: Deploy compact templates for simple products (-40% tokens)
3. **Context Routing**: Skip irrelevant generators based on HTML analysis (-30% processing)

**Advanced Improvements**:

1. **Multi-Language Support**: Enhanced German/international text processing
2. **Variant Intelligence**: Better grouping and variant relationship detection
3. **Cross-Context Validation**: Ensure consistency across generator outputs

**Future Enhancements**:

1. **Dynamic Prompting**: Adapt prompts based on product category
2. **Confidence Scoring**: Weight outputs based on extraction confidence
3. **Progressive Enhancement**: Layer basic → detailed → premium context levels

### 10. Implementation Testing Protocol

**Phase 1: Individual Generator Testing**

- Test each generator against rich-schema.json equivalent HTML
- Validate output format and field accuracy
- Measure token consumption and processing time

**Phase 2: Integration Testing**

- Run all 6 generators on same HTML input
- Test context coordination and field overlap
- Validate final schema.org output completeness

**Phase 3: Performance Optimization**

- Benchmark token efficiency improvements
- Test compact version fallbacks
- Validate quality maintenance under optimization

**Phase 4: Production Readiness**

- Test against diverse product types beyond apparel
- Validate multilingual content handling
- Stress test with high-volume processing

## Success Criteria

✅ **Coverage**: 80%+ of rich-schema.json fields extractable from equivalent HTML  
✅ **Accuracy**: 95%+ field extraction accuracy on available data  
✅ **Efficiency**: Complete processing under 7,200 token budget  
✅ **Quality**: Generated schema passes schema.org validation  
✅ **Scalability**: Framework handles diverse product categories

**Final Validation**: Successfully enrich shallow-schema.json to 80%+ richness of target rich-schema.json using context generator framework.
