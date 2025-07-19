# AI-Powered Schema.org Product Enrichment Platform

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

### Available Make Commands

```bash
make help              # Show all available commands
make backend-install   # Install backend dependencies
make backend-run       # Run backend server
make frontend-install  # Install frontend dependencies
make frontend-run      # Run frontend development server
make kill-backend-port # Kill process on backend port
make init              # Install all dependencies
```

## Product Brief

**Problem Statement:** E-commerce and product websites typically contain rich, unstructured data (descriptions, images, reviews, specifications) that LLMs struggle to process effectively. Meanwhile, existing schema.org Product markup on these pages is often sparse, missing critical structured data that could improve SEO, discoverability, and machine readability.

**Solution:** An AI-powered enrichment platform that transforms unstructured product page content into comprehensive, structured schema.org Product data through intelligent scraping, filtering, and LLM-based field extraction.

**Core Workflow:**

1. **Input:** User provides a product page URL
2. **Scraping:** System extracts HTML content and images from the target page
3. **Filtering:** Relevant product-specific content is isolated from noise (navigation, ads, etc.)
4. **AI Enrichment:** LLM processes filtered content to extract structured data for 23+ predefined schema.org properties including:
   - Core product data (name, description, brand, category)
   - Commercial data (price, currency, availability, condition)
   - Rich attributes (color, material, size, ratings, reviews)
   - Advanced properties (return policy, country of origin, audience targeting)
5. **Consensus Building:** Multiple AI suggestions are merged into a unified schema
6. **Human Validation:** HITL (Human-in-the-Loop) system for field-by-field approval/rejection
7. **Output:** Enriched, validated schema.org Product JSON returned to client

**Key Benefits:**

- Transforms unstructured web content into structured, SEO-friendly data
- Dramatically reduces manual effort in creating comprehensive product schemas
- Improves product discoverability through richer structured data
- Maintains data quality through human oversight and validation
- Supports 23+ schema.org Product properties out-of-the-box

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
│   │   └── html_extractor.py  # HTML context extraction service
│   ├── schemas/       # Pydantic data models
│   ├── prompts/       # AI prompt templates
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

## Enrichment Service

The **Enrichment Service** takes the output from the HTML Extractor (or similar input) and uses LLMs to fill in schema.org Product properties, returning a comprehensive, enriched product schema.

### Usage

```python
from enrichment.enricher import Enricher

# Example input matching the expected format
input_data = {
    "json_ld_schema": {
        "@context": "https://schema.org/",
        "@type": "Product"
    },
    "html_contexts": {
        "color": {
            "relevant_html_product_context": "These stylish shorts are available in a vibrant blue, perfect for summer adventures.",
            "product_name": "Test Backpack",
            "product_url": "https://example.com/product/123"
        },
        "brand": {
            "relevant_html_product_context": (
                "This product is proudly made by Patagonia, a renowned outdoor apparel company known for its commitment to quality, sustainability, and environmental activism. "
                "Patagonia products are designed for adventurers and outdoor enthusiasts who value durability, ethical manufacturing, and innovative design. "
                "The brand is recognized worldwide for its responsible sourcing of materials and dedication to reducing environmental impact. "
                "Choosing this product means supporting Patagonia's mission to create high-performance gear while protecting the planet."
            ),
            "product_name": "Test Backpack",
            "product_url": "https://example.com/product/123"
        },
        "keywords": {
            "relevant_html_product_context": """
                <div>
                    <h1>Test Backpack</h1>
                    <p>
                        The Test Backpack is designed for outdoor enthusiasts who love hiking, camping, and traveling.
                        With its durable water-resistant material, multiple compartments for organization, and ergonomic padded straps,
                        this backpack is perfect for long treks or daily commutes.
                        Whether you're exploring mountain trails, heading to the gym, or packing for a weekend getaway,
                        the Test Backpack offers versatility and comfort.
                        <ul>
                            <li>Spacious main compartment fits laptops up to 15 inches</li>
                            <li>Side pockets for water bottles or snacks</li>
                            <li>Reflective strips for safety during night hikes</li>
                            <li>Available in blue, black, and green</li>
                        </ul>
                        <div class=\"promo-banner\">Limited time offer: Free shipping on all outdoor gear!</div>
                        <footer>
                            <span>Customer reviews: \"Perfect for hiking and travel!\"</span>
                        </footer>
                    </p>
                </div>
            """,
            "product_name": "Test Backpack",
            "product_url": "https://example.com/product/123"
        }
    }
}

result = Enricher.enrich(input_data)
print(result)
print("Enriched product data:", result.data)
print("Not extracted properties:", result.not_extracted_properties)
print("Finished:", result.finished)
```

### Output

- `result.data`: The enriched schema.org Product dictionary
- `result.not_extracted_properties`: List of properties that could not be extracted
- `result.finished`: `True` if all properties were successfully extracted, else `False`

### Input/Output Format

**Input Format:**

```json
{
  "json_ld_schema": { ... },
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

**Output:**

- An `EnrichedProduct` object with `.data`, `.not_extracted_properties`, and `.finished` attributes.

---
