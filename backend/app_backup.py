import os
import json
import requests
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai_client import OpenAIClient
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

# Initialize OpenAI Client
openai_client = OpenAIClient()

# Initialize Extractor Service
extractor_service = ExtractorService()

class ComparisonRequest(BaseModel):
    products: List[Dict[str, Any]]

class ProductImprovement(BaseModel):
    category: str
    priority: str
    current: str
    suggested: str
    impact: str

class ProductAnalysisResponse(BaseModel):
    overall_score: int
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[ProductImprovement]
    seo_recommendations: List[str]
    missing_fields: List[str]
    conversion_tips: List[str]
    analysis: Optional[str] = None
    error: Optional[str] = None

class URLRequest(BaseModel):
    url: str



def validate_schema_org_product(product: Dict[str, Any]) -> bool:
    """Validate that the product data follows schema.org structure"""
    required_fields = ["@type", "name"]
    return all(field in product for field in required_fields)

def extract_products_from_data(data: Any) -> List[Dict[str, Any]]:
    """Extract product objects from complex nested schema.org data"""
    products = []
    
    def find_products(obj):
        if isinstance(obj, dict):
            if obj.get("@type") == "Product":
                products.append(obj)
            elif "hasVariant" in obj and isinstance(obj["hasVariant"], list):
                # Handle product variants
                for variant in obj["hasVariant"]:
                    if isinstance(variant, dict) and variant.get("@type") == "Product":
                        products.append(variant)
            # Recursively search in all dict values
            for value in obj.values():
                find_products(value)
        elif isinstance(obj, list):
            # Recursively search in all list items
            for item in obj:
                find_products(item)
    
    find_products(data)
    return products

async def process_uploaded_file(file: UploadFile) -> List[Dict[str, Any]]:
    """Process uploaded JSON file containing schema.org product data"""
    try:
        # Validate file type
        if not file.content_type.startswith('application/json') and not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="File must be JSON format")
        
        # Read and parse JSON content
        content = await file.read()
        
        try:
            data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Extract products from the data structure
        products = extract_products_from_data(data)
        
        if not products:
            raise HTTPException(status_code=400, detail="No valid product data found in JSON")
        
        return products
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/")
async def root():
    return {"message": "AI Product Analyzer API", "version": "1.0.0"}

# @app.post("/analyze")
# async def analyze_products(file: UploadFile = File(...)):
#     """Upload and analyze schema.org product data file"""
#     print(f"\n🔄 RECEIVED REQUEST: Analyzing file '{file.filename}'")
#     try:
#         # Process uploaded file
#         print(f"📁 Processing uploaded file: {file.filename}")
#         products_data = await process_uploaded_file(file)
#         print(f"✅ Found {len(products_data)} products to analyze")
        
#         # Analyze products with AI
#         results = []
        
#         for i, product in enumerate(products_data, 1):
#             try:
#                 print(f"🔍 Analyzing product {i}/{len(products_data)}: {product.get('name', 'Unknown')}")
                
#                 # Validate required fields
#                 if not validate_schema_org_product(product):
#                     print(f"⚠️  Product {i} failed validation - skipping")
#                     continue
                
#                 # Analyze with ChatGPT
#                 print(f"🤖 Sending product {i} to ChatGPT for analysis...")
#                 analysis = await analyze_product_data(product)
#                 print(f"✅ ChatGPT analysis complete for product {i} - Score: {analysis.get('overall_score', 'N/A')}/100")
                
#                 # Convert to response model
#                 response = ProductAnalysisResponse(**analysis)
#                 results.append(response)
                
#             except Exception as e:
#                 print(f"❌ Error analyzing product {i}: {str(e)}")
#                 # Add error response for failed analysis
#                 error_response = ProductAnalysisResponse(
#                     overall_score=0,
#                     strengths=[],
#                     weaknesses=["Analysis failed"],
#                     improvements=[],
#                     seo_recommendations=[],
#                     missing_fields=[],
#                     conversion_tips=[],
#                     error=str(e)
#                 )
#                 results.append(error_response)
        
#         print(f"🎉 ANALYSIS COMPLETE: Returning {len(results)} product analyses")
#         return results
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"💥 FATAL ERROR: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# @app.post("/compare")
# async def compare_products(request: ComparisonRequest):
#     """Compare multiple products and provide competitive analysis"""
#     try:
#         analysis = await compare_products_data(request.products)
#         return analysis
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")



# async def analyze_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Analyze a single product and provide improvement suggestions using OpenAI.
    
#     Args:
#         product: Product data to analyze
        
#     Returns:
#         Dict containing analysis results including score, strengths, weaknesses, improvements
#     """
#     try:
#         system_prompt = """You are a product data expert specializing in schema.org markup analysis. Analyze the provided product data and return a JSON response with:

# {
#   "overall_score": (number 0-100),
#   "strengths": [list of strings],
#   "weaknesses": [list of strings], 
#   "improvements": [
#     {
#       "category": "string",
#       "priority": "high|medium|low",
#       "current": "string",
#       "suggested": "string", 
#       "impact": "string"
#     }
#   ],
#   "seo_recommendations": [list of strings],
#   "missing_fields": [list of strings],
#   "conversion_tips": [list of strings]
# }"""

#         user_prompt = f"""Analyze this product data for schema.org compliance, SEO optimization, and conversion potential:

# {json.dumps(product, indent=2)}

# Focus on data completeness, structure quality, and business impact."""

#         response = openai_client.complete(
#             system_prompt=system_prompt,
#             user_prompt=user_prompt,
#             model="gpt-4o-mini",
#             temperature=0,
#             max_tokens=1500
#         )
        
#         try:
#             return json.loads(response)
#         except json.JSONDecodeError:
#             return {
#                 "overall_score": 50,
#                 "strengths": ["Data provided"],
#                 "weaknesses": ["Analysis parsing failed"],
#                 "improvements": [],
#                 "seo_recommendations": [],
#                 "missing_fields": [],
#                 "conversion_tips": [],
#                 "raw_response": response
#             }
            
#     except Exception as e:
#         return {
#             "overall_score": 0,
#             "strengths": [],
#             "weaknesses": ["Analysis failed"],
#             "improvements": [],
#             "seo_recommendations": [],
#             "missing_fields": [],
#             "conversion_tips": [],
#             "error": str(e)
#         }

# async def compare_products_data(products: List[Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Compare multiple products and provide competitive analysis using OpenAI.
    
#     Args:
#         products: List of product data to compare
        
#     Returns:
#         Dict containing comparison analysis
#     """
#     try:
#         system_prompt = """You are a competitive analysis expert. Compare the provided products and return a JSON response with:

# {
#   "summary": "string",
#   "best_product": "string",
#   "comparison_matrix": [
#     {
#       "product_name": "string",
#       "score": number,
#       "key_advantages": [strings],
#       "key_disadvantages": [strings]
#     }
#   ],
#   "recommendations": [strings],
#   "market_insights": [strings]
# }"""

#         products_json = json.dumps(products, indent=2)
#         user_prompt = f"""Compare these products and provide competitive analysis:

# {products_json}

# Focus on schema.org data quality, completeness, SEO potential, and competitive positioning."""

#         response = openai_client.complete(
#             system_prompt=system_prompt,
#             user_prompt=user_prompt,
#             model="gpt-4o-mini",
#             temperature=0,
#             max_tokens=1500
#         )
        
#         try:
#             return json.loads(response)
#         except json.JSONDecodeError:
#             return {
#                 "summary": "Comparison analysis completed",
#                 "best_product": "Unable to determine",
#                 "comparison_matrix": [],
#                 "recommendations": ["Review product data quality"],
#                 "market_insights": [],
#                 "raw_response": response
#             }
            
#     except Exception as e:
#         return {
#             "summary": "Comparison analysis failed",
#             "best_product": "Error",
#             "comparison_matrix": [],
#             "recommendations": [],
#             "market_insights": [],
#             "error": str(e)
#         }



async def get_product_context(productUrl: str):
    """Helper function: calls scrapeProductContext(productUrl) and returns formatted result"""
    from scraper.utils.product_context import scrapeProductContext
    
    # Call your scraper function with exact signature: scrapeProductContext(productUrl)
    result = await scrapeProductContext(productUrl)
    
    return {
        "product_html": result.get('relevant_html_product_context', ''),
        "images": {
            "url_main_image": result.get('images', {}).get('url_main_image', ''),
            "other_images": result.get('images', {}).get('other_images', [])
        },
        "json_ld_schema": result.get('json_ld_schema', None)
    }

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
        
        # Get scraped data from scraper
        scraped_data = await get_product_context(request.url)
        
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

# Old scraper endpoints removed - using scrapeProductContext instead

# @app.post("/scrape-main-product")
# async def scrape_main_product(request: URLRequest):
#     """Smart endpoint that focuses on extracting the main product only, filtering out suggestions"""
#     print(f"\n🎯 MAIN PRODUCT MODE: Analyzing {request.url}")
    
#     try:
#         # Import the focused main product scraper and context helper
#         from scraper.main import scrape_main_product as _scraper_main_product
#         from scraper.utils.product_context import scrapeProductContext as _scrape_product_context
        
#         print(f"🔍 Starting focused main product extraction for: {request.url}")
#         # Step 1: extract main product data (schema & analysis)
#         result = await _scraper_main_product(
#             domain_url=request.url,
#             headless=True,
#             delay=1.0
#         )
#         # Step 2: extract image URLs and HTML context by slug-based logic
#         context_data = await _scrape_product_context(request.url)
#         images = context_data.get('images', {})
#         html_context = context_data.get('relevant_html_product_context', '')
        
#         main_product = result.get('main_product')
#         all_products = result.get('all_products_found', [])
#         analysis = result.get('analysis', {})
        
#         print(f"🎯 MAIN PRODUCT ANALYSIS:")
#         print(f"   📦 Total products found: {len(all_products)}")
#         print(f"   🎯 Main product detected: {main_product is not None}")
#         print(f"   📊 Confidence: {analysis.get('main_product_confidence', 'unknown')}")
#         # Show extracted images and context (from product_context)
#         print(f"[API] scrape-main-product url_main_image: {images.get('url_main_image')}")
#         print(f"[API] scrape-main-product other_images: {images.get('other_images')}")
#         preview = html_context if len(html_context) < 200 else html_context[:200] + '...'
#         print(f"[API] scrape-main-product relevant_html_product_context: {preview}")
#         print(f"[API] scrape-main-product url_main_image: {images.get('url_main_image')}")
#         print(f"[API] scrape-main-product other_images: {images.get('other_images')}")
#         # HTML context preview
#         preview = html_context if len(html_context) < 200 else html_context[:200] + '...'
#         print(f"[API] scrape-main-product relevant_html_product_context: {preview}")
#         # Return focused main product data including images and context
#         return {
#             "url": request.url,
#             "status": "success",
#             "main_product": main_product,
#             "products_analyzed": len(all_products),
#             "all_products_found": all_products,
#             "analysis": analysis,
#             "images": images,
#             "relevant_html_product_context": html_context,
#             "detection_summary": {
#                 "main_product_found": main_product is not None,
#                 "confidence_level": analysis.get('main_product_confidence', 'unknown'),
#                 "total_products_on_page": len(all_products),
#                 "algorithm_used": "main_product_detector_v1"
#             }
#         }
        
#     except Exception as e:
#         print(f"💥 MAIN PRODUCT EXTRACTION ERROR: {str(e)}")
#         return {
#             "url": request.url,
#             "status": "error",
#             "error": str(e),
#             "main_product": None,
#             "products_analyzed": 0,
#             "analysis": {"error": str(e)}
#         }
    

# @app.options("/scrape-and-analyze")
# async def scrape_options():
#     """Handle CORS preflight for scrape-and-analyze endpoint"""
#     print("🔧 OPTIONS request received for /scrape-and-analyze")
#     return {"message": "OK"}

# # Old scraper options handlers removed

# @app.options("/scrape-main-product")
# async def scrape_main_product_options():
#     """Handle CORS preflight for scrape-main-product endpoint"""
#     print("🔧 OPTIONS request received for /scrape-main-product")
#     return {"message": "OK"}

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

@app.get("/health")
async def health_check():
    print("💓 Health check requested")
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }