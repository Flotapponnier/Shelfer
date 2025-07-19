# Prompt Generation System PRD

## Product Requirements Document for Schema.org Field Extraction

---

## Executive Summary

This PRD outlines the development of a sophisticated prompt generation system for extracting schema.org Product fields from unstructured web content. The system employs a three-tier agentic architecture: **Context Generators** → **Field Extractors** → **Validators**, utilizing advanced prompt engineering techniques to ensure reliable, non-hallucinatory data extraction.

**Key Goals:**

- Achieve >95% field extraction accuracy while maintaining 0% hallucination rate
- Build modular, reusable prompt templates for 23+ schema.org Product properties
- Create an intelligent context-routing system that matches optimal contexts to specific fields
- Implement robust validation mechanisms to ensure data quality

---

## Problem Statement

### Current Challenges

1. **Unstructured Data Complexity**: Product pages contain vast amounts of irrelevant information (navigation, ads, legal text) that confuses LLMs
2. **Field-Specific Context Requirements**: Different schema.org fields require different types of contextual information (e.g., price needs commercial context, brand needs company information)
3. **Hallucination Risk**: LLMs tend to generate plausible but incorrect data when insufficient information is available
4. **Inconsistent Extraction**: Single-shot prompts produce variable results across different product types and page structures

### Target Schema Properties

Based on analysis of `/data/rich-schema.json`, we target these 23+ schema.org Product properties:

- **Core**: name, description, brand, category, sku, gtin
- **Commercial**: offers.price, offers.priceCurrency, offers.availability, offers.itemCondition
- **Attributes**: color, material, size, image, aggregateRating, review
- **Advanced**: manufacturer, audience, keywords, hasMerchantReturnPolicy, countryOfLastProcessing, isFamilyFriendly, additionalType, negativeNotes, positiveNotes, nsn

---

## Solution Architecture

### Three-Tier Agentic System

#### Tier 1: Context Generation Prompts

**Purpose**: Generate specialized contexts from raw HTML/image data
**Contexts to Generate**:

- **Product Context**: Core product information, specifications, features
- **Commercial Context**: Pricing, availability, purchase conditions
- **Brand Context**: Company information, brand positioning, manufacturer details
- **User Experience Context**: Reviews, ratings, user feedback
- **Technical Context**: Specifications, materials, dimensions
- **Visual Context**: Image analysis results, visual product attributes
- **Page Structure Context**: Detected schema.org markup, metadata

#### Tier 2: Field Extraction Prompts

**Purpose**: Extract specific schema.org fields using relevant contexts
**Architecture**: One specialized prompt per field with configurable context inputs

#### Tier 3: Validation Prompts

**Purpose**: Validate extracted data for accuracy and prevent hallucinations
**Validation Types**: Format validation, logical consistency, confidence scoring

---

## Technical Requirements

### Prompt Engineering Techniques Integration

#### 1. System Role Assignment (Role-Play Prompting)

- **Research Backing**: 10.3% accuracy increase with favorable roles, 20-50% improvement with detailed descriptions
- **Implementation**: Each prompt tier gets domain-specific persona assignment
- **Context Generators**: "You are an expert web content analyst specializing in e-commerce product page structure"
- **Field Extractors**: "You are a meticulous data extraction specialist focusing on [specific field] identification"
- **Validators**: "You are a quality assurance expert ensuring data accuracy and completeness"

#### 2. Chain-of-Thought (CoT) Prompting

- **Research Backing**: 50-100% accuracy improvement, additional 12.2-18% with self-consistency
- **Implementation**: Step-by-step reasoning for complex field extraction
- **Best For**: Price extraction, availability determination, brand identification

#### 3. Few-Shot Prompting

- **Research Backing**: 26.28% improvement (Exact Match), 47.43% improvement (CodeBLEU)
- **Implementation**: 5-10 curated examples per field type
- **Example Sources**: `/data/rich-schema.json` and `/data/shallow-schema.json`

#### 4. Self-Ask and Meta-Prompting

- **Research Backing**: Improved reasoning through clarifying questions
- **Implementation**: Validators use self-ask to identify potential issues
- **Meta-Prompting**: Context generators create dynamic sub-questions based on content type

#### 5. Self-Consistency and Iterative Refinement

- **Research Backing**: 12% accuracy improvement with Lost-in-the-Middle mitigation
- **Implementation**: Multiple extraction attempts with consensus-building for ambiguous cases

#### 6. Emotion Prompting Enhancement

- **Research Backing**: 8-115% performance improvement, 10.9% boost in truthfulness
- **Implementation**: Strategic use of importance language ("This extraction is crucial for SEO success")

---

## Implementation Plan & Tasks

### Phase 1: Foundation Setup ✅ To Complete

- [x] **Task 1.1**: Analyze existing schema examples in `/data/` folder ✅ _COMPLETED_
- [x] **Task 1.2**: Define context-to-field mapping matrix (which contexts each field needs) ✅ _COMPLETED_
- [x] **Task 1.3**: Create prompt template structure with Markdown formatting ✅ _COMPLETED_
- [ ] **Task 1.4**: Establish evaluation criteria and success metrics
- [ ] **Task 1.5**: Set up prompt versioning and testing framework

### Phase 2: Context Generation Prompts ✅ *PHASE COMPLETED*

- [x] **Task 2.1**: Design Product Context Generator prompt ✅ _COMPLETED_
  - Extract core product information, features, specifications
  - Handle product variants and multiple SKUs
  - Identify product categories and types
- [x] **Task 2.2**: Design Commercial Context Generator prompt ✅ _COMPLETED_
  - Extract pricing information and currency
  - Identify availability status and stock information
  - Detect purchase conditions and shipping details
- [x] **Task 2.3**: Design Brand Context Generator prompt ✅ _COMPLETED_
  - Extract brand name and manufacturer information
  - Identify company background and positioning
  - Handle private label vs. brand name scenarios
- [x] **Task 2.4**: Design User Experience Context Generator prompt ✅ _COMPLETED_
  - Extract reviews and ratings data
  - Summarize user feedback and sentiment
  - Identify common praise/complaint themes
- [x] **Task 2.5**: Design Technical Context Generator prompt ✅ *COMPLETED*
  - Extract technical specifications
  - Identify materials, dimensions, and attributes
  - Handle variant-specific technical details
- [x] **Task 2.6**: Design Visual Context Generator prompt ✅ *COMPLETED*
  - Analyze product images for attributes
  - Extract visual properties (color, style, features)
  - Identify product presentation and context
- [x] **Task 2.7**: Test and refine context generation prompts ✅ *COMPLETED*
  - Validate against `/data/rich-schema.json` examples
  - Ensure comprehensive context coverage
  - Optimize for token efficiency

### Phase 3: Field Extraction Prompts ✅ To Complete

- [ ] **Task 3.1**: Core Field Extractors (6 prompts)
  - name, description, brand, category, sku, gtin
- [ ] **Task 3.2**: Commercial Field Extractors (4 prompts)
  - offers.price, offers.priceCurrency, offers.availability, offers.itemCondition
- [ ] **Task 3.3**: Attribute Field Extractors (6 prompts)
  - color, material, size, image, aggregateRating, review
- [ ] **Task 3.4**: Advanced Field Extractors (7 prompts)
  - manufacturer, audience, keywords, hasMerchantReturnPolicy, countryOfLastProcessing, isFamilyFriendly, additionalType
- [ ] **Task 3.5**: Configure context routing for each field
  - Define which contexts each field extractor receives
  - Optimize context combinations for accuracy
- [ ] **Task 3.6**: Implement CoT reasoning for complex fields
  - Add step-by-step extraction logic
  - Include confidence assessment steps
- [ ] **Task 3.7**: Add few-shot examples for each field type
  - Curate 5-10 examples per field from existing data
  - Include edge cases and challenging scenarios

### Phase 4: Validation System ✅ To Complete

- [ ] **Task 4.1**: Design Format Validation prompts
  - Validate data types (strings, numbers, URLs, enums)
  - Check schema.org compliance
  - Ensure proper formatting
- [ ] **Task 4.2**: Design Logical Consistency Validation prompts
  - Cross-field validation (price vs. availability)
  - Detect contradictory information
  - Verify contextual appropriateness
- [ ] **Task 4.3**: Design Confidence Scoring prompts
  - Assess extraction confidence levels
  - Identify uncertain or ambiguous cases
  - Flag potential hallucinations
- [ ] **Task 4.4**: Implement Self-Ask validation
  - Add clarifying questions for edge cases
  - Create decision trees for complex scenarios
- [ ] **Task 4.5**: Build consensus mechanisms
  - Multiple extraction attempts for uncertain cases
  - Majority voting for validation decisions

### Phase 5: Integration & Testing ✅ To Complete

- [ ] **Task 5.1**: Create prompt orchestration system
  - Context generation → field extraction → validation pipeline
  - Error handling and retry mechanisms
- [ ] **Task 5.2**: Implement configuration system
  - Field-specific context routing configuration
  - Adjustable confidence thresholds
  - Prompt version management
- [ ] **Task 5.3**: Build evaluation framework
  - Automated testing against known examples
  - Performance metrics tracking
  - A/B testing capabilities for prompt variations
- [ ] **Task 5.4**: Conduct comprehensive testing
  - Test with `/data/rich-schema.json` examples
  - Validate against various product types
  - Measure accuracy and hallucination rates
- [ ] **Task 5.5**: Performance optimization
  - Token usage optimization
  - Latency reduction strategies
  - Cost-effectiveness analysis

### Phase 6: Production Readiness ✅ To Complete

- [ ] **Task 6.1**: Create prompt documentation
  - Template usage guidelines
  - Context routing documentation
  - Field extraction examples
- [ ] **Task 6.2**: Build monitoring and alerting
  - Track extraction success rates
  - Monitor hallucination indicators
  - Alert on validation failures
- [ ] **Task 6.3**: Implement continuous improvement
  - Feedback loop integration
  - Prompt performance analytics
  - Automated prompt optimization suggestions

---

## Success Metrics

### Primary KPIs

- **Field Extraction Accuracy**: >95% correct field identification
- **Hallucination Rate**: <2% (fields marked as "none" when data unavailable)
- **Context Relevance Score**: >90% (contexts contain relevant information for target fields)
- **Validation Accuracy**: >98% (validation correctly identifies good/bad extractions)

### Secondary KPIs

- **Token Efficiency**: <2000 tokens average per field extraction
- **Latency**: <5 seconds end-to-end extraction time
- **Coverage**: Successfully extract ≥15 fields per product page
- **Consistency**: <5% variance in extraction results across multiple runs

---

## Risk Assessment & Mitigation

### High-Risk Areas

1. **Prompt Injection Vulnerabilities**

   - _Risk_: Malicious content could manipulate extraction results
   - _Mitigation_: Input sanitization, prompt isolation techniques

2. **Context Window Limitations**

   - _Risk_: Large product pages exceed model context limits
   - _Mitigation_: Intelligent content chunking, priority-based context selection

3. **Model Drift Over Time**
   - _Risk_: Model updates may affect prompt performance
   - _Mitigation_: Automated regression testing, prompt versioning

### Medium-Risk Areas

1. **Edge Case Handling**

   - _Risk_: Unusual product types may not extract well
   - _Mitigation_: Comprehensive test coverage, fallback mechanisms

2. **Multi-language Support**
   - _Risk_: Non-English content may extract poorly
   - _Mitigation_: Language detection, translated context generation

---

## Technical Architecture Decisions

### Prompt Template Structure

```markdown
# System Role

You are a [specific expert role]...

## Task Definition

Your task is to [specific objective with CoT steps]...

## Context & Specifics

[Relevant domain context and importance statements]...

## Examples (Few-Shot)

[3-5 curated examples showing desired outputs]...

## Critical Reminders

[Key constraints and edge case handling]...
```

### Context Routing Matrix

| Field Type | Product | Commercial | Brand | UX  | Technical | Visual | Metadata |
| ---------- | ------- | ---------- | ----- | --- | --------- | ------ | -------- |
| name       | ✓       |            |       |     |           | ✓      | ✓        |
| price      |         | ✓          |       |     |           |        |          |
| brand      | ✓       |            | ✓     |     |           |        | ✓        |
| color      | ✓       |            |       |     | ✓         | ✓      |          |
| rating     |         |            |       | ✓   |           |        |          |

---

## Future Enhancements

### V2 Features

- **Adaptive Context Selection**: ML-based optimization of context routing
- **Cross-Field Validation**: Advanced consistency checking across all extracted fields
- **Uncertainty Quantification**: Probabilistic confidence scores for each extraction
- **Multi-Modal Integration**: Enhanced image analysis for visual product attributes

### V3 Features

- **Real-Time Learning**: Prompt optimization based on validation feedback
- **Domain Specialization**: Industry-specific prompt variants (fashion, electronics, etc.)
- **Multilingual Support**: Native extraction for non-English content

---

## Appendix

### Research References

1. **Role-Play Prompting**: Shanahan, McDonell, & Reynolds - "Role Play with Large Language Models"
2. **Chain-of-Thought**: Jason Wei et al. - "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
3. **Few-Shot Learning**: Tom B. Brown et al. - "Language Models are Few-Shot Learners"
4. **Self-Consistency**: Xuezhi Wang et al. - "Self-Consistency Improves Chain of Thought Reasoning"
5. **Lost-in-the-Middle**: Nelson F. Liu et al. - "Lost in the Middle: How Language Models Use Long Contexts"
6. **Emotion Prompting**: Cheng Li et al. - "Large Language Models Understand and Can be Enhanced by Emotional Stimuli"

### Prompt Engineering Resources

- **Comprehensive Guide**: [promptingguide.ai](https://www.promptingguide.ai/)
- **Advanced Techniques**: Chain-of-Thought, ReAct, Self-Ask, Meta-Prompting
- **Best Practices**: Markdown formatting, context optimization, validation strategies

---

_Document Version: 1.0_  
_Last Updated: January 2025_  
_Next Review: Phase 1 Completion_
