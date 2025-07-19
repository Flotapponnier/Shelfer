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
│   ├── main.py        # API endpoints
│   └── requirements.txt
└── README.md
```