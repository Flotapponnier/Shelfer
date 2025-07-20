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
from enrichment.enricher import AsyncEnricher

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
        
        # Debug: Print full product_html content without truncation
        full_product_html = scraped_data.get('product_html', '')
        print(f"[API] DEBUG - Full product_html length: {len(full_product_html)}")
        print(f"[API] DEBUG - Full product_html content:")
        print(f"{full_product_html}")
        print(f"[API] DEBUG - End of full product_html")
        
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
        
        # Step 3: Run enricher to convert extracted contexts into schema.org properties
        print(f"✨ Step 3: Running schema enrichment...")
        
        # Prepare product metadata for enricher (clean, no redundancy)
        product_metadata = {
            "product_name": None,  # TODO: Could extract from HTML or let enricher infer
            "product_url": request.url,
            "json_ld_schema": extraction_result.get("json_ld_schema")
        }
        
        # Get HTML contexts from extraction results  
        html_contexts = extraction_result.get("html_contexts", {})
        
        try:
            # Call enricher with clean interface
            enricher = AsyncEnricher()
            enriched_schema, not_extracted_properties = await enricher.enrich(product_metadata, html_contexts)

            # Log enrichment summary
            enriched_count = len(html_contexts) - len(not_extracted_properties)
            enrichment_success_rate = enriched_count / len(html_contexts) if html_contexts else 0

            print(f"📈 Enrichment completed:")
            print(f"   • Properties enriched: {enriched_count}/{len(html_contexts)}")
            print(f"   • Enrichment success rate: {enrichment_success_rate:.1%}")
            print(f"   • Failed properties: {not_extracted_properties}")
            print(f"   • Final schema complete: {len(not_extracted_properties) == 0}")

            enrichment_metadata = {
                "properties_processed": len(html_contexts),
                "properties_enriched": enriched_count,
                "properties_failed": len(not_extracted_properties),
                "failed_properties": not_extracted_properties,
                "not_extracted_properties": not_extracted_properties,
                "success_rate": enrichment_success_rate
            }
            
        except Exception as e:
            print(f"⚠️ Enrichment failed: {str(e)}")
            # Continue with extraction results only
            enriched_schema = None
            enrichment_metadata = {
                "error": str(e),
                "properties_processed": len(html_contexts),
                "properties_enriched": 0,
                "success_rate": 0,
            }
        
        # Return comprehensive results
        response = {
            "url": request.url,
            "status": "success",
            "scraped_data": scraped_data,
            "extraction_results": extraction_result,
            "extraction_metadata": metadata
        }
        print(enriched_schema)
        original_schema = product_metadata["json_ld_schema"]
        # Add enrichment results if successful
        
        response["original_product_schema"] = original_schema
        response["enriched_product_schema"] = enriched_schema
        print(response)
        return response
        
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