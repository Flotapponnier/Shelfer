import os
import json
import requests
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai_client import OpenAIClient

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

class SchemaValidationRequest(BaseModel):
    schema_data: Dict[str, Any]

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

@app.post("/analyze")
async def analyze_products(file: UploadFile = File(...)):
    """Upload and analyze schema.org product data file"""
    print(f"\n🔄 RECEIVED REQUEST: Analyzing file '{file.filename}'")
    try:
        # Process uploaded file
        print(f"📁 Processing uploaded file: {file.filename}")
        products_data = await process_uploaded_file(file)
        print(f"✅ Found {len(products_data)} products to analyze")
        
        # Analyze products with AI
        results = []
        
        for i, product in enumerate(products_data, 1):
            try:
                print(f"🔍 Analyzing product {i}/{len(products_data)}: {product.get('name', 'Unknown')}")
                
                # Validate required fields
                if not validate_schema_org_product(product):
                    print(f"⚠️  Product {i} failed validation - skipping")
                    continue
                
                # Analyze with ChatGPT
                print(f"🤖 Sending product {i} to ChatGPT for analysis...")
                analysis = await chatgpt_model.analyze_product(product)
                print(f"✅ ChatGPT analysis complete for product {i} - Score: {analysis.get('overall_score', 'N/A')}/100")
                
                # Convert to response model
                response = ProductAnalysisResponse(**analysis)
                results.append(response)
                
            except Exception as e:
                print(f"❌ Error analyzing product {i}: {str(e)}")
                # Add error response for failed analysis
                error_response = ProductAnalysisResponse(
                    overall_score=0,
                    strengths=[],
                    weaknesses=["Analysis failed"],
                    improvements=[],
                    seo_recommendations=[],
                    missing_fields=[],
                    conversion_tips=[],
                    error=str(e)
                )
                results.append(error_response)
        
        print(f"🎉 ANALYSIS COMPLETE: Returning {len(results)} product analyses")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 FATAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/compare")
async def compare_products(request: ComparisonRequest):
    """Compare multiple products and provide competitive analysis"""
    try:
        analysis = await chatgpt_model.compare_products(request.products)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.post("/validate-schema")
async def validate_schema(request: SchemaValidationRequest):
    """Validate schema.org markup and suggest improvements"""
    try:
        validation = await chatgpt_model.validate_schema(request.schema_data)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema validation failed: {str(e)}")

async def get_product_context(productUrl: str):
    """Helper function: calls scrapeProductContext(productUrl) and returns formatted result"""
    from scraper.utils.product_context import scrapeProductContext
    
    # Call your scraper function with exact signature: scrapeProductContext(productUrl)
    result = await scrapeProductContext(productUrl)
    
    # Ensure exact format: { relevantHtmlProductContext, images: { urlMainimage, otherMainImages }, schema.org }
    return {
        "relevantHtmlProductContext": result.get('relevantHtmlProductContext', ''),
        "images": {
            "urlMainimage": result.get('images', {}).get('urlMainimage', ''),
            "otherMainImages": result.get('images', {}).get('otherMainImages', [])
        },
        "schema.org": result.get('schema.org', None)
    }

@app.post("/enrich-product-schema")
async def enrich_product_schema(request: URLRequest):
    """Product enrichment endpoint: URL → scrapeProductContext → enrichment pipeline"""
    print(f"\n🔄 RECEIVED ENRICHMENT REQUEST: {request.url}")
    
    try:
        print(f"🌐 Step 1: Extracting product context from {request.url}...")
        
        # Call helper function to get product context
        productContext = await get_product_context(request.url)
        
        # Log the results
        print(f"[API] enrich-product-schema urlMainimage: {productContext['images']['urlMainimage']}")
        print(f"[API] enrich-product-schema otherMainImages: {productContext['images']['otherMainImages']}")
        preview = productContext['relevantHtmlProductContext']
        preview = preview if len(preview) < 200 else preview[:200] + '...'
        print(f"[API] enrich-product-schema relevantHtmlProductContext: {preview}")
        
        # TODO: Add enrichment pipeline here - for now return scraper result
        # This is where HTML extractor and enricher would be called
        print(f"🧠 Step 2: AI enrichment pipeline (TODO - returning raw scraper data for now)")
        
        # Return the product context (enrichment pipeline will be added later)
        return {
            "url": request.url,
            "status": "success",
            "productContext": productContext
        }
        
    except Exception as e:
        print(f"💥 FATAL ERROR in enrich-product-schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Product enrichment failed: {str(e)}")

# Old scraper endpoints removed - using scrapeProductContext instead

@app.post("/scrape-main-product")
async def scrape_main_product(request: URLRequest):
    """Smart endpoint that focuses on extracting the main product only, filtering out suggestions"""
    print(f"\n🎯 MAIN PRODUCT MODE: Analyzing {request.url}")
    
    try:
        # Import the focused main product scraper and context helper
        from scraper.main import scrape_main_product as _scraper_main_product
        from scraper.utils.product_context import scrapeProductContext as _scrape_product_context
        
        print(f"🔍 Starting focused main product extraction for: {request.url}")
        # Step 1: extract main product data (schema & analysis)
        result = await _scraper_main_product(
            domain_url=request.url,
            headless=True,
            delay=1.0
        )
        # Step 2: extract image URLs and HTML context by slug-based logic
        context_data = await _scrape_product_context(request.url)
        images = context_data.get('images', {})
        html_context = context_data.get('relevantHtmlProductContext', '')
        
        main_product = result.get('main_product')
        all_products = result.get('all_products_found', [])
        analysis = result.get('analysis', {})
        
        print(f"🎯 MAIN PRODUCT ANALYSIS:")
        print(f"   📦 Total products found: {len(all_products)}")
        print(f"   🎯 Main product detected: {main_product is not None}")
        print(f"   📊 Confidence: {analysis.get('main_product_confidence', 'unknown')}")
        # Show extracted images and context (from product_context)
        print(f"[API] scrape-main-product urlMainimage: {images.get('urlMainimage')}")
        print(f"[API] scrape-main-product otherMainImages: {images.get('otherMainImages')}")
        preview = html_context if len(html_context) < 200 else html_context[:200] + '...'
        print(f"[API] scrape-main-product relevantHtmlProductContext: {preview}")
        print(f"[API] scrape-main-product urlMainimage: {images.get('urlMainimage')}")
        print(f"[API] scrape-main-product otherMainImages: {images.get('otherMainImages')}")
        # HTML context preview
        preview = html_context if len(html_context) < 200 else html_context[:200] + '...'
        print(f"[API] scrape-main-product relevantHtmlProductContext: {preview}")
        # Return focused main product data including images and context
        return {
            "url": request.url,
            "status": "success",
            "main_product": main_product,
            "products_analyzed": len(all_products),
            "all_products_found": all_products,
            "analysis": analysis,
            "images": images,
            "relevantHtmlProductContext": html_context,
            "detection_summary": {
                "main_product_found": main_product is not None,
                "confidence_level": analysis.get('main_product_confidence', 'unknown'),
                "total_products_on_page": len(all_products),
                "algorithm_used": "main_product_detector_v1"
            }
        }
        
    except Exception as e:
        print(f"💥 MAIN PRODUCT EXTRACTION ERROR: {str(e)}")
        return {
            "url": request.url,
            "status": "error",
            "error": str(e),
            "main_product": None,
            "products_analyzed": 0,
            "analysis": {"error": str(e)}
        }
    

@app.options("/scrape-and-analyze")
async def scrape_options():
    """Handle CORS preflight for scrape-and-analyze endpoint"""
    print("🔧 OPTIONS request received for /scrape-and-analyze")
    return {"message": "OK"}

# Old scraper options handlers removed

@app.options("/scrape-main-product")
async def scrape_main_product_options():
    """Handle CORS preflight for scrape-main-product endpoint"""
    print("🔧 OPTIONS request received for /scrape-main-product")
    return {"message": "OK"}

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