# Task 1.2: Context-to-Field Mapping Matrix
## Defining Context Requirements for Schema.org Field Extraction

---

## Executive Summary

This document defines the **context routing configuration** for our three-tier prompt system. Based on Task 1.1 analysis, we map which contexts each of the 23 target schema.org fields requires for optimal extraction. This matrix serves as the blueprint for our intelligent context-routing system.

---

## Context Definitions

### 1. **Product Context** 🎯
**Purpose**: Core product information, specifications, features, categories
**Sources**: Product descriptions, feature lists, specification tables, category breadcrumbs, product titles
**Key Elements**: Product name, type, category, features, specifications, materials, dimensions

### 2. **Commercial Context** 💰
**Purpose**: Pricing, availability, purchase conditions, policies
**Sources**: Price displays, stock indicators, shipping info, return policies, terms of service
**Key Elements**: Prices, currencies, availability status, conditions, shipping, returns

### 3. **Brand Context** 🏢
**Purpose**: Brand information, manufacturer details, company background
**Sources**: Brand descriptions, about pages, manufacturer info, company details
**Key Elements**: Brand name, manufacturer, company history, origin country, certifications

### 4. **User Experience Context** ⭐
**Purpose**: Customer feedback, reviews, ratings, sentiment analysis
**Sources**: Review sections, rating displays, customer testimonials, Q&A sections
**Key Elements**: Ratings, reviews, customer feedback, pros/cons, sentiment

### 5. **Technical Context** ⚙️
**Purpose**: Technical specifications, materials, manufacturing details
**Sources**: Technical spec sheets, material lists, manufacturing info, compliance data
**Key Elements**: Materials, dimensions, technical specs, certifications, standards

### 6. **Visual Context** 📷
**Purpose**: Visual product attributes from images
**Sources**: Product images, image alt text, visual analysis
**Key Elements**: Colors, styles, visual features, packaging, presentation

### 7. **Page Structure Context** 📄
**Purpose**: Existing schema.org markup, metadata, structured data
**Sources**: HTML meta tags, existing JSON-LD, microdata, page structure
**Key Elements**: Existing schema, meta tags, structured data, page hierarchy

---

## Context-to-Field Mapping Matrix

### **Priority Legend**
- 🔴 **PRIMARY**: Essential context - field extraction likely fails without it
- 🟡 **SECONDARY**: Supporting context - improves accuracy and completeness  
- 🟢 **OPTIONAL**: Supplementary context - provides additional validation or enhancement

---

| Field | Product | Commercial | Brand | UX | Technical | Visual | Page Structure | Complexity |
|-------|---------|------------|-------|----|-----------|---------| --------------|------------|
| **offers.price** | 🟢 | 🔴 | 🟢 | 🟢 | | | 🟡 | **Low** |
| **offers.priceCurrency** | | 🔴 | 🟡 | | | | 🟡 | **Low** |
| **offers.availability** | 🟡 | 🔴 | | | | | 🟡 | **Medium** |
| **description** | 🔴 | 🟢 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | **Medium** |
| **image** | 🟡 | | | | | 🔴 | 🟡 | **Low** |
| **brand** | 🟡 | | 🔴 | | | | 🟡 | **Low** |
| **offers.itemCondition** | 🟡 | 🔴 | | 🟡 | | | 🟡 | **Medium** |
| **color** | 🟡 | | | | | 🔴 | 🟡 | **Medium** |
| **material** | 🔴 | | 🟡 | 🟡 | 🔴 | 🟡 | 🟡 | **High** |
| **aggregateRating** | 🟡 | | | 🔴 | | | 🟡 | **Medium** |
| **review** | 🟡 | | | 🔴 | | | 🟡 | **High** |
| **category** | 🔴 | | 🟡 | | | | 🟡 | **Medium** |
| **keywords** | 🔴 | | 🟡 | 🟡 | 🟡 | | 🟡 | **High** |
| **manufacturer** | 🟡 | | 🔴 | | 🟡 | | 🟡 | **Medium** |
| **size** | 🔴 | | | | 🟡 | 🟡 | 🟡 | **Medium** |
| **audience** | 🔴 | | 🟡 | 🟡 | | 🟡 | 🟡 | **High** |
| **additionalType** | 🔴 | | 🟡 | | 🟡 | | 🟡 | **High** |
| **hasMerchantReturnPolicy** | | 🔴 | 🟡 | 🟡 | | | 🟡 | **High** |
| **negativeNotes** | 🟡 | | | 🔴 | | | 🟡 | **High** |
| **positiveNotes** | 🟡 | | | 🔴 | | | 🟡 | **High** |
| **nsn** | 🟡 | | 🟡 | | 🔴 | | 🟡 | **Medium** |
| **countryOfLastProcessing** | 🟡 | | 🔴 | | 🔴 | | 🟡 | **High** |
| **isFamilyFriendly** | 🔴 | | | 🟡 | | | 🟡 | **High** |

---

## Detailed Field-Context Mappings

### **GROUP A: Low Complexity Fields** (3 fields)

#### 1. **offers.price** 💰
- **PRIMARY**: Commercial Context 🔴
  - *Why*: Prices are typically in price display sections
  - *Sources*: Price tags, shopping cart, offer sections
- **SECONDARY**: Page Structure Context 🟡
  - *Why*: May exist in existing schema markup
- **OPTIONAL**: Product Context, UX Context, Brand Context 🟢
  - *Why*: Additional validation and currency context

#### 2. **offers.priceCurrency** 💱
- **PRIMARY**: Commercial Context 🔴
  - *Why*: Currency symbols/codes appear with prices
  - *Sources*: Price displays, payment sections
- **SECONDARY**: Brand Context, Page Structure Context 🟡
  - *Why*: Geographic context helps determine likely currency

#### 3. **image** 🖼️
- **PRIMARY**: Visual Context 🔴
  - *Why*: Image URLs are typically in img tags or galleries
  - *Sources*: Image galleries, product photos
- **SECONDARY**: Page Structure Context 🟡
  - *Why*: May exist in existing schema markup
- **OPTIONAL**: Product Context 🟢
  - *Why*: Additional context for image relevance

---

### **GROUP B: Medium Complexity Fields** (8 fields)

#### 4. **offers.availability** 📦
- **PRIMARY**: Commercial Context 🔴
  - *Why*: Stock status displayed in purchase sections
  - *Sources*: "In Stock", "Out of Stock", availability indicators
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: Product variants may have different availability

#### 5. **description** 📝
- **PRIMARY**: Product Context 🔴
  - *Why*: Product descriptions are core product content
  - *Sources*: Product description sections, feature lists
- **OPTIONAL**: All other contexts 🟢
  - *Why*: Descriptions can be enhanced with brand, technical, UX insights

#### 6. **brand** 🏷️
- **PRIMARY**: Brand Context 🔴
  - *Why*: Brand information is typically explicit
  - *Sources*: Brand names, logos, manufacturer info
- **SECONDARY**: Page Structure Context 🟡
  - *Why*: May exist in existing schema markup
- **OPTIONAL**: Product Context 🟢
  - *Why*: Brand may appear in product titles

#### 7. **offers.itemCondition** 🔄
- **PRIMARY**: Commercial Context 🔴
  - *Why*: Condition info appears in purchase sections
  - *Sources*: "New", "Used", "Refurbished" indicators
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: Product context may indicate if items are typically new/used
- **OPTIONAL**: UX Context 🟢
  - *Why*: Reviews may mention condition

#### 8. **color** 🎨
- **PRIMARY**: Visual Context 🔴
  - *Why*: Colors are visual attributes best extracted from images/swatches
  - *Sources*: Color swatches, product images, variant selectors
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: Color may be mentioned in product names/descriptions

#### 9. **aggregateRating** ⭐
- **PRIMARY**: User Experience Context 🔴
  - *Why*: Ratings are displayed in review sections
  - *Sources*: Star ratings, score displays, review summaries
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: May exist in existing schema or be mentioned in product context

#### 10. **manufacturer** 🏭
- **PRIMARY**: Brand Context 🔴
  - *Why*: Manufacturer info typically with brand details
  - *Sources*: Brand pages, manufacturer sections, about info
- **SECONDARY**: Product Context, Technical Context, Page Structure Context 🟡
  - *Why*: May appear in technical specs or product descriptions

#### 11. **size** 📏
- **PRIMARY**: Product Context 🔴
  - *Why*: Size information in product specifications
  - *Sources*: Size charts, variant selectors, specifications
- **SECONDARY**: Technical Context, Visual Context, Page Structure Context 🟡
  - *Why*: Technical specs may include dimensions, images may show scale

---

### **GROUP C: High Complexity Fields** (12 fields)

#### 12. **material** 🧵
- **PRIMARY**: Product Context, Technical Context 🔴
  - *Why*: Materials listed in product specs and technical details
  - *Sources*: Material lists, technical specifications, feature descriptions
- **SECONDARY**: Brand Context, UX Context, Visual Context, Page Structure Context 🟡
  - *Why*: Brand quality info, customer reviews mention materials, visual texture

#### 13. **review** 📄
- **PRIMARY**: User Experience Context 🔴
  - *Why*: Reviews are explicitly in review sections
  - *Sources*: Customer reviews, testimonials, feedback sections
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: Product context helps understand what reviews are about

#### 14. **category** 📂
- **PRIMARY**: Product Context 🔴
  - *Why*: Categories in navigation, breadcrumbs, product classifications
  - *Sources*: Category breadcrumbs, navigation menus, product classifications
- **SECONDARY**: Brand Context, Page Structure Context 🟡
  - *Why*: Brand specialization, existing category markup

#### 15. **keywords** 🔑
- **PRIMARY**: Product Context 🔴
  - *Why*: Keywords derived from product features, names, descriptions
  - *Sources*: Product titles, feature lists, marketing copy
- **SECONDARY**: Brand Context, UX Context, Technical Context, Page Structure Context 🟡
  - *Why*: Brand keywords, customer language, technical terms, meta keywords

#### 16. **audience** 👥
- **PRIMARY**: Product Context 🔴
  - *Why*: Target audience inferred from product type, marketing language
  - *Sources*: Marketing copy, product positioning, demographic indicators
- **SECONDARY**: Brand Context, UX Context, Visual Context, Page Structure Context 🟡
  - *Why*: Brand positioning, customer demographics, visual style cues

#### 17. **additionalType** 🏷️
- **PRIMARY**: Product Context 🔴
  - *Why*: Additional product classifications from detailed product info
  - *Sources*: Product specifications, detailed classifications, feature lists
- **SECONDARY**: Brand Context, Technical Context, Page Structure Context 🟡
  - *Why*: Brand-specific types, technical classifications, existing markup

#### 18. **hasMerchantReturnPolicy** ↩️
- **PRIMARY**: Commercial Context 🔴
  - *Why*: Return policy information in commercial/policy sections
  - *Sources*: Return policy pages, terms of service, purchase conditions
- **SECONDARY**: Brand Context, UX Context, Page Structure Context 🟡
  - *Why*: Brand reputation for returns, customer experience mentions

#### 19. **negativeNotes** ❌
- **PRIMARY**: User Experience Context 🔴
  - *Why*: Negative feedback explicitly in reviews and customer comments
  - *Sources*: Customer reviews, complaints, negative feedback sections
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: Product context helps understand what negatives relate to

#### 20. **positiveNotes** ✅
- **PRIMARY**: User Experience Context 🔴
  - *Why*: Positive feedback explicitly in reviews and testimonials
  - *Sources*: Customer reviews, testimonials, positive feedback highlights
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: Product context helps understand what positives relate to

#### 21. **nsn** 🔢
- **PRIMARY**: Technical Context 🔴
  - *Why*: NSN (National Stock Number) is a technical identifier
  - *Sources*: Technical specifications, compliance data, military/government specs
- **SECONDARY**: Product Context, Brand Context, Page Structure Context 🟡
  - *Why*: May appear in product specs, brand compliance info

#### 22. **countryOfLastProcessing** 🌍
- **PRIMARY**: Brand Context, Technical Context 🔴
  - *Why*: Manufacturing/processing location in brand or technical info
  - *Sources*: "Made in" labels, manufacturing info, brand origin details
- **SECONDARY**: Product Context, Page Structure Context 🟡
  - *Why*: Product specs may include origin, existing markup

#### 23. **isFamilyFriendly** 👨‍👩‍👧‍👦
- **PRIMARY**: Product Context 🔴
  - *Why*: Family-friendly indicators inferred from product type and content
  - *Sources*: Age recommendations, safety information, content warnings
- **SECONDARY**: UX Context, Page Structure Context 🟡
  - *Why*: Customer reviews may mention family use, existing content ratings

---

## Context Usage Statistics

### **Context Utilization Summary**
| Context | Primary Uses | Secondary Uses | Total Fields | Utilization % |
|---------|--------------|----------------|--------------|---------------|
| **Product Context** | 10 | 13 | 23 | **100%** |
| **Commercial Context** | 6 | 0 | 6 | **26%** |
| **Brand Context** | 4 | 10 | 14 | **61%** |
| **User Experience Context** | 4 | 8 | 12 | **52%** |
| **Technical Context** | 3 | 7 | 10 | **43%** |
| **Visual Context** | 2 | 4 | 6 | **26%** |
| **Page Structure Context** | 0 | 23 | 23 | **100%** |

### **Key Insights**
1. **Product Context** is universal - needed by all 23 fields
2. **Page Structure Context** provides secondary support for all fields
3. **Commercial Context** is highly specialized - only needed for 6 fields but critical
4. **User Experience Context** is essential for review/rating fields
5. **Technical Context** is crucial for specialized fields (materials, NSN, manufacturing)

---

## Implementation Guidelines

### **Context Generation Order**
1. **Page Structure Context** (parse existing markup first)
2. **Product Context** (core product information)
3. **Commercial Context** (pricing and purchase info)
4. **Brand Context** (company and manufacturer info)
5. **Visual Context** (image analysis)
6. **Technical Context** (specifications and technical details)
7. **User Experience Context** (reviews and ratings)

### **Context Routing Configuration**
```json
{
  "field_context_mapping": {
    "offers.price": {
      "primary": ["commercial"],
      "secondary": ["page_structure"],
      "optional": ["product", "ux", "brand"]
    },
    "material": {
      "primary": ["product", "technical"],
      "secondary": ["brand", "ux", "visual", "page_structure"],
      "optional": []
    }
    // ... additional field mappings
  }
}
```

### **Token Optimization Strategy**
- **Primary contexts**: Always included, full content
- **Secondary contexts**: Included with summarized content (50% token reduction)
- **Optional contexts**: Included only if token budget allows (25% of full content)

---

## Validation Rules

### **Context Consistency Checks**
1. **Cross-Context Validation**: Brand names should match across Brand and Product contexts
2. **Price-Currency Alignment**: Currency should match geographic context from Brand info
3. **Review-Rating Consistency**: Aggregate ratings should align with review sentiment
4. **Technical-Product Alignment**: Technical specs should match product descriptions

### **Missing Context Handling**
- If **Primary** context missing: Return "none" for field
- If **Secondary** context missing: Proceed with reduced confidence
- If **Optional** context missing: No impact on extraction

---

## Next Steps for Task 1.3

This mapping matrix provides the foundation for:
1. **Prompt Template Structure**: Each field extractor template will reference required contexts
2. **Context Generation Priority**: High-utilization contexts get priority in development
3. **Token Budget Allocation**: Primary contexts get larger token allocations
4. **Validation Framework**: Cross-context validation rules defined

---

*Context-Field Mapping Completed: Task 1.2 ✅*  
*Ready for Task 1.3: Prompt template structure with Markdown formatting* 