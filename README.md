# AI-Powered Schema.org Product Enrichment Platform

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
│   ├── main.py        # API endpoints
│   └── requirements.txt
└── README.md
```

## Quick Start

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000 to use the application.

Frontend: Next.js app with a clean SEO analyzer interface
Backend: FastAPI server with /analyze endpoint
Structure: Organized folders with proper architecture

To run:
Backend: cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port
8000
Frontend: cd frontend && npm install && npm run dev
