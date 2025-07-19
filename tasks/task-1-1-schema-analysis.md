# Task 1.1: Schema Analysis Report

## Analysis of Existing Schema Examples in `/data/` Folder

---

## Executive Summary

This analysis examines three schema files to understand the current state of schema.org Product data and identify patterns for our extraction system. The analysis reveals a significant gap between basic schema markup (`shallow-schema.json`) and comprehensive product data (`rich-schema.json`), confirming the need for our AI-powered enrichment system.

---

## File Overview

### 1. `shallow-schema.json` (13 lines)

- **Type**: Basic Product schema
- **Completeness**: ~15% of target fields present
- **Use Case**: Represents typical sparse schema.org markup found on product pages

### 2. `rich-schema.json` (348 lines)

- **Type**: Comprehensive ProductGroup with variants
- **Completeness**: ~65% of target fields present
- **Use Case**: Represents our enrichment target - what we want to achieve

### 3. `richest-schema.json` (1 line)

- **Content**: "TBD" (placeholder)
- **Status**: Not yet implemented

---

## Target Fields Analysis

Based on the user-specified 23 target fields, here's the current coverage and extraction complexity:

### ✅ **Present in Rich Schema** (15/23 fields)

| Field                  | Example Value                                             | Data Type      | Extraction Complexity                |
| ---------------------- | --------------------------------------------------------- | -------------- | ------------------------------------ |
| `offers.price`         | `29.99`                                                   | Number         | **Low** - Usually explicit           |
| `offers.priceCurrency` | `"EUR"`                                                   | String (ISO)   | **Low** - Usually explicit           |
| `offers.availability`  | `"https://schema.org/InStock"`                            | Schema.org URL | **Medium** - Needs status mapping    |
| `description`          | `"Robuste Trekkingshorts..."`                             | Text           | **Medium** - Rich vs. short variants |
| `image`                | `"https://www.bfgcdn.com/..."`                            | URL            | **Low** - Usually explicit           |
| `brand`                | `{"@type": "Brand", "name": "Stoic"}`                     | Object         | **Low** - Usually explicit           |
| `offers.itemCondition` | `"https://schema.org/NewCondition"`                       | Schema.org URL | **Medium** - Needs condition mapping |
| `color`                | `"Black"`, `"Forest Green"`                               | String         | **Medium** - Variant-specific        |
| `size`                 | `"34"`, `"36"`, `"38"`                                    | String         | **Medium** - Variant-specific        |
| `audience`             | `{"@type": "PeopleAudience", "suggestedGender": "women"}` | Object         | **High** - Complex inference         |

### ❌ **Missing from Current Schema** (13/23 fields)

These fields represent our primary extraction targets:

| Field                     | Expected Data Type | Extraction Complexity | Context Requirement     |
| ------------------------- | ------------------ | --------------------- | ----------------------- |
| `material`                | String/Array       | **High**              | Technical Context       |
| `aggregateRating`         | Object             | **Medium**            | User Experience Context |
| `review`                  | Array              | **High**              | User Experience Context |
| `category`                | String/Array       | **Medium**            | Product Context         |
| `keywords`                | Array              | **High**              | Product + SEO Context   |
| `manufacturer`            | String             | **Medium**            | Brand Context           |
| `additionalType`          | URL/String         | **High**              | Product Context         |
| `hasMerchantReturnPolicy` | Boolean/Object     | **High**              | Commercial Context      |
| `negativeNotes`           | String             | **High**              | User Experience Context |
| `positiveNotes`           | String             | **High**              | User Experience Context |
| `nsn`                     | String             | **Medium**            | Technical Context       |
| `countryOfLastProcessing` | String             | **High**              | Brand/Technical Context |
| `isFamilyFriendly`        | Boolean            | **High**              | Content Analysis        |

---

## Key Data Patterns

### 1. **Product Hierarchy Structure**

```json
ProductGroup (parent)
├── hasVariant[] (children)
│   ├── Product (variant 1: Black, size 34)
│   ├── Product (variant 2: Forest Green, size 34)
│   └── Product (variant N: various combinations)
└── offers (per variant)
```

### 2. **Field Distribution Patterns**

- **Group Level**: `name`, `description`, `brand`, `audience`
- **Variant Level**: `color`, `size`, `sku`, `gtin`, `image`
- **Offer Level**: `price`, `priceCurrency`, `availability`, `itemCondition`

### 3. **Schema.org URL Patterns**

- Conditions: `https://schema.org/NewCondition`
- Availability: `https://schema.org/InStock`, `https://schema.org/OutOfStock`
- Audience: Structured objects with typed properties

### 4. **Multilingual Considerations**

- Product content in German (Bergfreunde.de)
- Demonstrates need for language-agnostic extraction

---

## Context Requirements Analysis

Based on the missing fields, our context generators need to extract:

### **Product Context** (Required for 8 fields)

- `category`, `keywords`, `additionalType`, `material`
- **Sources**: Product specifications, feature lists, category breadcrumbs

### **User Experience Context** (Required for 4 fields)

- `aggregateRating`, `review`, `negativeNotes`, `positiveNotes`
- **Sources**: Review sections, rating displays, customer feedback

### **Commercial Context** (Required for 1 field)

- `hasMerchantReturnPolicy`
- **Sources**: Return policy pages, terms of service

### **Brand/Technical Context** (Required for 3 fields)

- `manufacturer`, `nsn`, `countryOfLastProcessing`
- **Sources**: Product specifications, technical details, brand information

### **Content Analysis Context** (Required for 1 field)

- `isFamilyFriendly`
- **Sources**: Content analysis, age recommendations, safety information

---

## Extraction Complexity Assessment

### **Low Complexity** (3 fields)

Fields typically present in existing markup:

- `offers.price`, `offers.priceCurrency`, `image`

### **Medium Complexity** (8 fields)

Fields requiring structured extraction from common page elements:

- `offers.availability`, `description`, `brand`, `offers.itemCondition`, `color`, `size`, `aggregateRating`, `manufacturer`

### **High Complexity** (12 fields)

Fields requiring deep content analysis and inference:

- `material`, `review`, `category`, `keywords`, `audience`, `additionalType`, `hasMerchantReturnPolicy`, `negativeNotes`, `positiveNotes`, `nsn`, `countryOfLastProcessing`, `isFamilyFriendly`

---

## Few-Shot Training Examples

### **Available Examples** (from current data)

- ✅ E-commerce outdoor gear (Bergfreunde.de)
- ✅ Product variants with size/color combinations
- ✅ Multi-currency pricing (EUR)
- ✅ Stock status variations (InStock/OutOfStock)
- ✅ Brand structure examples

### **Missing Example Types**

- ❌ Electronics/technology products
- ❌ Different price ranges (luxury, budget)
- ❌ Products with reviews/ratings
- ❌ Complex material specifications
- ❌ Different market verticals

---

## Data Quality Insights

### **Strengths**

1. **Consistent Structure**: Well-formed schema.org markup
2. **Complete Variant Handling**: Comprehensive size/color matrix
3. **Real-World Complexity**: Actual e-commerce data with edge cases
4. **Proper Typing**: Correct schema.org types and relationships

### **Gaps for Enrichment**

1. **Missing Review Data**: No aggregateRating or review fields
2. **Limited Technical Specs**: No material, manufacturer details
3. **No Category Information**: Missing product categorization
4. **No Policy Information**: No return policy or family-friendly indicators

---

## Recommendations for Prompt System

### **High-Priority Context Generators**

1. **Product Specification Parser**: Extract technical details, materials, features
2. **Review Aggregator**: Parse customer feedback and ratings
3. **Category Classifier**: Identify product categories and types
4. **Policy Extractor**: Find return policies and safety information

### **Field-Specific Extraction Strategy**

1. **Variant-Aware Processing**: Handle size/color combinations properly
2. **Multi-Language Support**: Extract from German content effectively
3. **Schema.org URL Mapping**: Convert text to proper schema.org URLs
4. **Confidence Scoring**: Identify when information is uncertain

### **Validation Priorities**

1. **Cross-Variant Consistency**: Ensure brand/description consistency across variants
2. **Price-Currency Matching**: Validate currency codes with geographic context
3. **Availability Logic**: Ensure stock status makes sense with pricing
4. **Image URL Validation**: Verify image URLs are accessible and relevant

---

## Next Steps for Task 1.2

Based on this analysis, the context-to-field mapping matrix should prioritize:

1. **Product Context** → Most missing fields (8 targets)
2. **User Experience Context** → High-value fields (4 targets)
3. **Brand/Technical Context** → Complex but valuable (3 targets)

---

_Analysis completed: Task 1.1 ✅_  
_Document prepared for Task 1.2: Context-to-field mapping matrix_
