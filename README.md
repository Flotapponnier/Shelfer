# AI-Powered Schema.org Product Enrichment Platform

## Product Brief

**Problem Statement:** E-commerce and product websites typically contain rich, unstructured data (descriptions, images, reviews, specifications) that LLMs struggle to process effectively. Meanwhile, existing schema.org Product markup on these pages is often sparse, missing critical structured data that could improve SEO, discoverability, and machine readability.

**Solution:** An AI-powered enrichment platform that transforms unstructured product page content into comprehensive, structured schema.org Product data through intelligent scraping, filtering, and LLM-based field extraction.

**Core Workflow (Fully Automated Pipeline):**

1. **Input:** User provides a product page URL via `/enrich-product-schema` API
2. **Scraping:** System extracts HTML content, images, and existing JSON-LD from the target page
3. **Extraction:** AI-powered extractors identify relevant HTML contexts for 32 schema.org properties:
   - **HTML Extractor:** Processes 22 properties from product HTML content
   - **Image Extractor:** Analyzes 10 visual properties using GPT-4o vision model
4. **Enrichment:** LLM converts extracted contexts into structured schema.org properties:
   - Core product data (name, description, brand, category)
   - Commercial data (price, currency, availability, condition) 
   - Rich attributes (color, material, size, ratings, reviews)
   - Advanced properties (return policy, country of origin, audience targeting)
5. **Response:** Returns comprehensive results including:
   - Raw scraped data, extraction results, and enriched schema.org JSON
   - Detailed metadata and success rates for each pipeline stage

**Key Benefits:**

- Transforms unstructured web content into structured, SEO-friendly data
- Dramatically reduces manual effort in creating comprehensive product schemas
- Improves product discoverability through richer structured data
- Maintains data quality through human oversight and validation
- Supports 23+ schema.org Product properties out-of-the-box

## Quick Start

### Prerequisites

Make sure you have the following installed:

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Node.js](https://nodejs.org/) (for frontend)
- [Make](https://www.gnu.org/software/make/) (for build automation)

### Option 1: Using Makefile (Recommended)

The easiest way to get started is using the provided Makefile:

```bash
# Install all dependencies (backend & frontend)
make init

# Run the backend server (FastAPI on port 8000)
make backend-run

# In a new terminal, run the frontend (Next.js on port 3000)
make frontend-run
```

### Option 2: Manual Setup

#### Backend (FastAPI)

```bash
cd backend
uv sync  # Install Python dependencies using uv
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Test the Complete Pipeline

```bash
# Test the full pipeline: Scraper → Extractor → Enricher
curl -X POST http://localhost:8000/enrich-product-schema \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product-page"}' | jq .

# Check just the enriched schema
curl -X POST http://localhost:8000/enrich-product-schema \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product-page"}' | jq .enriched_schema
```

### Available Make Commands

```bash
make help                     # Show all available commands
make backend-install          # Install backend dependencies
make backend-run              # Run backend server
make frontend-install         # Install frontend dependencies
make frontend-run             # Run frontend development server
make kill-backend-port        # Kill process on backend port
make init                     # Install all dependencies
make test-html-extractor      # Run HTML extractor service test
make test-image-extractor     # Run image extractor service test
make test-all                 # Run all extractor service tests
```

**Technical Architecture:** Next.js frontend with Python FastAPI backend, featuring modular scraper, enricher, and merger components integrated with OpenAI's GPT models.

## Project Structure

```
├── frontend/          # Next.js React application
│   ├── src/
│   │   └── app/
│   │       └── page.tsx   # Main SEO analyzer interface
│   └── package.json
├── backend/           # FastAPI Python backend
│   ├── services/      # Core business logic
│   │   ├── html_extractor.py   # HTML context extraction service
│   │   └── image_extractor.py  # Image analysis extraction service
│   ├── schemas/       # Pydantic data models
│   ├── prompts/       # AI prompt templates
│   ├── tests/         # Test scripts and documentation
│   │   ├── README.md               # Test instructions and results
│   │   ├── test_image_extractor.py # Image extractor service test
│   │   └── test_html_extractor.py  # HTML extractor service test
│   ├── main.py        # API endpoints
│   └── requirements.txt
└── README.md
```

## HTML Extractor Service

The **HTML Extractor Service** is a core component that processes scraped product data and identifies relevant HTML contexts for each schema.org property using OpenAI's GPT models.

### Usage

```python
from services.html_extractor import HtmlExtractorService
from schemas.product import ScraperInput, ProductImages

# Initialize the service
extractor = HtmlExtractorService()

# Prepare input data from your scraper
scraper_input = ScraperInput(
    product_html="<div class='product'>...</div>",  # Cleaned HTML from scraper
    images=ProductImages(
        url_main_image="https://example.com/main.jpg",
        other_main_images=["https://example.com/alt1.jpg"]
    ),
    json_ld_schema={"@type": "Product", "name": "..."}  # Optional existing schema
)

# Extract HTML contexts for all 22 target properties
result = extractor.extract_html_contexts(scraper_input)

# Output ready for enricher
print(f"Processed {len(result.html_contexts)} properties")
# result.html_contexts contains relevant HTML for each property
# result.json_ld_schema contains forwarded schema data
```

### Supported Properties

The extractor identifies HTML contexts for 22 schema.org Product properties from HTML:

**Core Properties:** `offers.price`, `offers.priceCurrency`, `offers.availability`, `description`, `brand`, `offers.itemCondition`

**Product Details:** `color`, `material`, `size`, `category`, `keywords`, `manufacturer`, `audience`, `additionalType`

**Reviews & Ratings:** `aggregateRating`, `review`, `positiveNotes`, `negativeNotes`

**Business Info:** `hasMerchantReturnPolicy`, `nsn`, `countryOfLastProcessing`, `isFamilyFriendly`

**Note:** The `image` property requires separate image analysis and is not handled by this HTML extractor.

### Input/Output Format

**Input Format:**

```json
{
  "product_html": "<html>cleaned product page content</html>",
  "images": {
    "url_main_image": "https://example.com/main.jpg",
    "other_main_images": ["https://example.com/alt1.jpg"]
  },
  "json_ld_schema": {...}
}
```

**Output Format:**

```json
{
  "json_ld_schema": {...},
  "html_contexts": {
    "offers.price": {
      "relevant_html_product_context": "<span class='price'>$29.99</span>"
    },
    "description": {
      "relevant_html_product_context": "<div class='desc'>Product details...</div>"
    }
  }
}
```

The output is designed to be directly consumed by the enricher component in the next stage of the pipeline.

## Testing the Services

Both extractor services include comprehensive test suites to validate functionality and demonstrate usage.

### Quick Testing with Makefile

```bash
# Test HTML extraction (22 properties from product HTML)
make test-html-extractor

# Test image extraction (10 properties from product images)
make test-image-extractor

# Run both tests
make test-all
```

### Manual Testing

```bash
# Test HTML extractor
cd backend
uv run python tests/test_html_extractor.py

# Test image extractor
cd backend
uv run python tests/test_image_extractor.py
```

### Test Results Overview

- **HTML Extractor**: 100% success rate (22/22 properties) extracting from rich product HTML
- **Image Extractor**: 100% success rate (10/10 properties) analyzing product images with GPT-4o vision
- **Combined Coverage**: 32 total schema.org properties across text and visual analysis

For detailed test documentation, results, and troubleshooting, see [`backend/tests/README.md`](backend/tests/README.md).

## Image Extractor Service

The **Image Extractor Service** complements the HTML extractor by analyzing product images using GPT-4o vision model to extract visual schema.org properties that cannot be determined from HTML alone.

### Usage

```python
from services.image_extractor import ImageExtractorService
from schemas.product import ScraperInput, ProductImages

# Initialize the service
image_extractor = ImageExtractorService()

# Prepare input data with product images
scraper_input = ScraperInput(
    product_html="<div>...</div>",  # Not used by image extractor
    images=ProductImages(
        url_main_image="https://example.com/product-main.jpg",
        other_main_images=["https://example.com/variant1.jpg", "https://example.com/detail.jpg"]
    ),
    json_ld_schema={"@type": "Product", "name": "Product Name"}
)

# Extract visual properties from images
result = image_extractor.extract_image_contexts(
    scraper_input=scraper_input,
    product_name="Product Name",
    product_url="https://example.com/product"
)

# Output compatible with enricher
print(f"Processed {len(result)} visual properties")
# result is Dict[str, HtmlContext] with visual data extracted from images
```

### Supported Visual Properties

The image extractor identifies 10 schema.org properties that can be determined from product images:

**Visual Characteristics:** `color`, `material`, `size`

**Product Information:** `image`, `brand`, `category`, `additionalType`

**Quality Assessment:** `offers.itemCondition`, `positiveNotes`, `negativeNotes`

### Features

- **GPT-4o Vision Integration**: Uses OpenAI's most advanced vision model for accurate analysis
- **Multi-Image Processing**: Analyzes main image first, then processes additional images for incomplete properties
- **Safety Handling**: Detects and handles safety refusals with fallback prompts
- **Error Resilience**: Gracefully handles invalid URLs, network issues, and processing errors
- **Format Support**: Supports common image formats (JPG, PNG, GIF, BMP, WebP)

### Input/Output Format

**Input**: Same `ScraperInput` format as HTML extractor, but focuses on the `images` field

**Output**: `Dict[str, HtmlContext]` where each property contains extracted visual information

```json
{
  "color": {
    "relevant_html_product_context": "Red with black accents"
  },
  "material": {
    "relevant_html_product_context": "Premium leather with metal hardware"
  },
  "brand": {
    "relevant_html_product_context": "Nike logo visible on product"
  }
}
```

### Integration with HTML Extractor

Both services can be used together to provide comprehensive property extraction:

```python
from services.html_extractor import HtmlExtractorService
from services.image_extractor import ImageExtractorService

# Extract from both HTML and images
html_contexts = html_extractor.extract_html_contexts(scraper_input)
image_contexts = image_extractor.extract_image_contexts(scraper_input, product_name, product_url)

# Combine results (32 total properties: 22 from HTML + 10 from images)
all_contexts = {**html_contexts.html_contexts, **image_contexts}
```

## Enrichment Service

The **Enrichment Service** takes the output from the HTML and Image Extractors and uses LLMs to convert extracted contexts into schema.org Product properties, returning a comprehensive, enriched product schema. **Now fully integrated into the main API pipeline.**

### Integration in API Pipeline

The enricher is **automatically called** in the `/enrich-product-schema` endpoint as the final step:

```
URL Input → Scraper → Extractor (HTML + Images) → Enricher → Enhanced Response
```

### Standalone Usage

```python
from enrichment.enricher import Enricher

# Clean, separated inputs (no redundancy!)
product_metadata = {
    "product_name": "Tennis Socks Premium",
    "product_url": "https://snocks.com/products/tennissocken",
    "json_ld_schema": {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": "Tennis Socks Premium"
    }
}

# HTML contexts from extractor output (clean, focused on content)
html_contexts = {
    "color": {
        "relevant_html_product_context": "Available in Black, White, and Blue"
    },
    "brand": {
        "relevant_html_product_context": "SNOCKS - Premium Athletic Wear"
    },
    "material": {
        "relevant_html_product_context": "Made from premium cotton blend with moisture-wicking properties"
    }
}

# Call enricher with clean interface
result = Enricher.enrich(
    product_metadata=product_metadata,
    html_contexts=html_contexts
)

print("Enriched product data:", result.enriched_json_ld_schema)
print("Original product data:", result.original_json_ld_schema)
print("Not extracted properties:", result.not_extracted_properties)
print("Finished:", result.finished)
```

### New Clean Interface

**Key Improvements:**
- ✅ **No Redundancy**: Product metadata provided once, not repeated 32 times
- ✅ **Separation of Concerns**: Product-level and property-level data are separated
- ✅ **Better Performance**: Smaller payloads, cleaner code

### Input/Output Format

**Input Format (Standalone):**

```python
# Product metadata (provided once)
product_metadata = {
    "product_name": "Product Name",
    "product_url": "https://example.com/product", 
    "json_ld_schema": {...}  # Optional existing schema
}

# HTML contexts (clean, no repetition)
html_contexts = {
    "offers.price": {
        "relevant_html_product_context": "<span class='price'>$29.99</span>"
    },
    "description": {
        "relevant_html_product_context": "<div class='desc'>Product details...</div>"
    }
}
```

**Output:**

- An `EnrichedProduct` object with `.enriched_json_ld_schema`, `.original_json_ld_schema`, `.not_extracted_properties`, and `.finished` attributes.

### Enhanced API Response Format

When using `/enrich-product-schema`, you now get comprehensive results:

```json
{
  "url": "https://example.com/product",
  "status": "success",
  "scraped_data": {...},              // Raw scraper output
  "extraction_results": {...},        // Extractor output (32 properties)
  "extraction_metadata": {            // Extraction statistics
    "html_properties_extracted": 22,
    "image_properties_extracted": 10,
    "overall_success_rate": 0.75
  },
  "enriched_schema": {                // NEW: Final enriched schema.org
    "@context": "https://schema.org/",
    "@type": "Product",
    "name": "Product Name",
    "offers": {"price": "29.99"},
    "enriched": true
  },
  "original_schema": {...},           // NEW: Original JSON-LD found
  "enrichment_metadata": {            // NEW: Enrichment statistics
    "properties_processed": 25,
    "properties_enriched": 20,
    "success_rate": 0.80,
    "schema_complete": false,
    "failed_properties": ["size", "weight"]
  }
}
```

## Product Context Scraper

The scraper component is the first stage of our enrichment pipeline, responsible for extracting raw content from product pages. It uses a dual-approach strategy for maximum reliability:

### Primary Method: OpenAI-Powered Extraction

**How it works:**
1. **Page Loading**: Uses Playwright to load the product page with full JavaScript rendering
2. **Content Cleaning**: Removes scripts, styles, and extracts clean text from `document.body.innerText`
3. **Smart Truncation**: Limits text to 20,000 characters to avoid OpenAI token limits
4. **AI Analysis**: Sends clean text to GPT-4 with structured prompt:
   ```
   "Given the text of a product page, extract the main product details 
   (name, price, description, features, variants, availability) and return 
   a JSON object: { name, price, description, features[], variants[], availability }"
   ```
5. **Validation**: Detects when OpenAI returns non-product content or errors

**OpenAI Success Criteria:**
- Returns valid JSON with product information
- No error messages or "not a product page" responses
- Content length > 10 characters

### Fallback Method: HTML-Based Extraction

**When triggered:**
- OpenAI token limit exceeded
- OpenAI detects non-product content (e.g., cookie pages, privacy policies)
- API errors or empty responses

**How it works:**
1. **CSS Selector Extraction**: Uses proven selectors to find product elements:
   - **Name**: `h1.product-title`, `h1.product-name`, `h1`
   - **Price**: `.price`, `.product-price`, currency validation with regex
   - **Description**: `.product-description`, `.summary`, length validation
   - **Features**: `.features li`, `.specifications li`
   - **Availability**: `.stock`, `.availability`

2. **Image Processing**: 
   - Extracts product images using `ProductImageExtractor`
   - Prioritizes main product images over thumbnails
   - Handles lazy-loaded and high-resolution variants

3. **JSON-LD Schema**: 
   - Parses structured data from `<script type="application/ld+json">`
   - Identifies Product schemas using `@type` validation
   - Extracts schema.org properties as backup data

4. **Image Prioritization**:
   - Uses JSON-LD schema images as primary source when available
   - Falls back to scraped images from page analysis
   - Maintains original scraped images as alternatives

**Output Format:**
```json
{
  "relevant_html_product_context": "Raw HTML or OpenAI JSON",
  "images": {
    "url_main_image": "https://...",
    "other_images": ["https://...", "https://..."]
  },
  "json_ld_schema": [/* Parsed schema.org objects */],
  "raw_page_text": "Clean page text" // Only when OpenAI is used
}
```

### Error Handling

The scraper implements comprehensive error handling:

1. **Page Loading Issues**: Retries with different wait conditions
2. **Content Extraction Failures**: Multiple fallback text extraction methods
3. **OpenAI Failures**: Automatic fallback to HTML-based approach
4. **Complete Failure**: Returns `"No content. All techniques failed."`

### Usage in Pipeline

The scraper output feeds directly into the extraction pipeline:
- **HTML context** → HTML Extractor (22 properties)
- **Images** → Image Extractor (10 visual properties)  
- **JSON-LD** → Direct schema.org property mapping
- **Raw text** → Context for enrichment validation

This dual-approach ensures reliable product data extraction across diverse e-commerce platforms, from simple HTML sites to complex JavaScript-heavy stores.

## Scraper Core Components

The scraper operates through 3 main components that work together to extract comprehensive product data:

### 1. Schema.org Parsing & Product Prediction

**Purpose**: Discovers and validates existing structured data on product pages.

**Algorithm**:
```python
# Extract JSON-LD scripts from page
jsonld_scripts = await JSONLDExtractor().extract_jsonld_from_page(page)
parsed = parse_json_ld_scripts(jsonld_scripts)
schema_images = [o for o in parsed if _is_product_schema(o)]
```

**Product Prediction Logic** (`_is_product_schema`):
1. **Primary Check**: Looks for `@type: "Product"` in JSON-LD objects
2. **Type Validation**: Handles string, list, and URL format types (`http://schema.org/product`)
3. **Fallback Prediction**: Analyzes product-specific fields like `offers`, `sku`, `mpn`, `gtin13`
4. **Pattern Detection**: Validates common product patterns (`name` + `offers` combination)

**What it extracts**: Complete schema.org Product objects with properties like name, price, description, brand, offers, images, etc.

### 2. Main Product Image Extraction

**Purpose**: Identifies the primary product image using intelligent CSS selectors and quality assessment.

**Selector Strategy**:
```python
main_image_selectors = [
    '.product-image-main img',     # Dedicated main containers
    '.product-hero img',           # Hero/banner images  
    '.featured-image img',         # Featured displays
    '[data-main-image] img',       # Data attribute marked
    '.product-cover img'           # Cover images
]
```

**Quality Assessment**:
- **Resolution Priority**: Extracts highest quality from `<picture>` srcsets
- **Lazy Loading**: Handles `data-src`, `data-srcset` attributes
- **Quality Keywords**: Prioritizes images with indicators like `large`, `original`, `zoom`

**Output**: Single main product image URL optimized for quality and relevance.

### 3. Other Images (Gallery) Extraction

**Purpose**: Collects additional product images from galleries, thumbnails, and related image sets.

**Discovery Method**:
```python
thumbnail_selectors = [
    '.product-thumbnails img', '.product-thumbs img',
    '.image-gallery img', '.product-images-thumbs img', 
    '.thumbnail img', '.gallery-thumb img'
]
```

**Processing**:
- **Gallery Containers**: Searches product image containers and carousels
- **Thumbnail Resolution**: Follows thumbnail links to discover full-size versions  
- **Deduplication**: Removes duplicates and variants of the same image
- **Schema Integration**: Merges with schema.org images when available

**Output**: Array of additional product images for comprehensive visual representation.

## Scraper's Role in Project

The scraper serves as the **data foundation layer** that feeds into the AI enrichment pipeline:

**Input**: Product URLs → **Scraper** → **Output**: Structured data
- `raw_page_text`: Clean text for AI analysis
- `relevant_html_product_context`: OpenAI JSON or HTML fallback
- `images`: {main image + other images array}  
- `json_ld_schema`: Discovered schema.org objects

This structured output then flows to the **Extractor Service** (22 HTML properties + 10 image properties) and **Enricher** (final schema.org generation).

---
