"""
Clean FastAPI Application - Focused on Product Enrichment

Only includes the components actually being used:
- /enrich-product-schema endpoint (main functionality)
- Supporting helper functions
- Basic FastAPI setup
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from services.extractor_service import ExtractorService

load_dotenv()

app = FastAPI(title="AI Product Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Extractor Service (only service we actually use)
extractor_service = ExtractorService()

# Pydantic models (only the ones actually used)
class URLRequest(BaseModel):
    url: str

# No helper functions - keeping controller truly lightweight

@app.post("/enrich-product-schema")
async def enrich_product_schema(request: URLRequest):
    """
    Product enrichment endpoint: URL → scrapeProductContext → extractor pipeline
    
    Workflow:
    1. Scrapes product page using get_product_context()
    2. Extracts 32 schema.org properties (22 from HTML + 10 from images)  
    3. Returns enriched data ready for further processing
    """
    print(f"\n🔄 RECEIVED ENRICHMENT REQUEST: {request.url}")
    
    try:
        print(f"🌐 Step 1: Extracting product context from {request.url}...")
        
        # Get scraped data directly from scraper
        from scraper.utils.product_context import scrapeProductContext
        scraper_result = await scrapeProductContext(request.url)
        
        # Debug: Log the raw scraper result
        print(f"🔍 DEBUG: Raw scraper result keys: {list(scraper_result.keys()) if scraper_result else 'None'}")
        print(f"🔍 DEBUG: Raw scraper result: {scraper_result}")
        
        # Format scraped data for extractor service
        scraped_data = {
            "product_html": scraper_result.get('relevant_html_product_context', ''),
            "images": {
                "url_main_image": scraper_result.get('images', {}).get('url_main_image', ''),
                "other_images": scraper_result.get('images', {}).get('other_images', [])
            },
            "json_ld_schema": scraper_result.get('json_ld_schema', None)
        }
        
        # Log the scraped results
        print(f"[API] enrich-product-schema url_main_image: {scraped_data['images']['url_main_image']}")
        print(f"[API] enrich-product-schema other_images: {scraped_data['images']['other_images']}")
        preview = scraped_data.get('product_html', '')
        preview = preview if len(preview) < 200 else preview[:200] + '...'
        print(f"[API] enrich-product-schema product_html: {preview}")
        
        print(f"✅ Scraped data obtained successfully")
        
        # Step 2: Run extraction pipeline (HTML + Image extractors)
        print(f"🧠 Step 2: Running AI extraction pipeline...")
        
        extraction_result = await extractor_service.extract_product_data(
            scraped_data=scraped_data,
            product_name=None,  # Could extract from HTML if needed
            product_url=request.url
        )
        
        # Log extraction summary
        metadata = extraction_result.get("processing_metadata", {})
        total_extracted = metadata.get("total_properties_extracted", 0)
        total_properties = metadata.get("total_properties", 0)
        success_rate = metadata.get("overall_success_rate", 0)
        
        print(f"📊 Extraction completed:")
        print(f"   • Properties extracted: {total_extracted}/{total_properties}")
        print(f"   • Success rate: {success_rate:.1%}")
        print(f"   • HTML properties: {metadata.get('html_properties_extracted', 0)}")
        print(f"   • Image properties: {metadata.get('image_properties_extracted', 0)}")
        
        # Return enriched product data
        # TODO: Instead of returning we need to pass the data on to the "enricher" here
        return {
            "url": request.url,
            "status": "success",
            "scraped_data": scraped_data,
            "extraction_results": extraction_result,
            "processing_metadata": metadata
        }
        
    except Exception as e:
        print(f"💥 FATAL ERROR in enrich-product-schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Product enrichment failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    print("💓 Health check requested")
    return {
        "status": "healthy",
        "extractor_service_ready": True
    }

# CORS middleware (needed for frontend integration)
@app.middleware("http")
async def cors_handler(request, call_next):
    """Custom CORS middleware for debugging"""
    print(f"🌐 Request: {request.method} {request.url}")
    
    if request.method == "OPTIONS":
        print("🔧 Handling OPTIONS request")
        from fastapi import Response
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    
    response = await call_next(request)
    return response 