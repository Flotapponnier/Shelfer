import os
import json
import requests
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from models.chatgpt import ChatGPTModel

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

# Initialize ChatGPT Model
chatgpt_model = ChatGPTModel()

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

@app.post("/scrape-and-analyze")
async def scrape_and_analyze(request: URLRequest):
    """Complete workflow: URL → Real Scraper → ChatGPT Analysis"""
    print(f"\n🔄 RECEIVED SCRAPE REQUEST: {request.url}")
    
    try:
        # Step 1: Use the real scraper to extract product data
        print(f"🌐 Step 1: Scraping {request.url} with real scraper...")
        
        # Import scraper (do this here to avoid startup issues)
        from scraper.main import scrape_domain
        
        # Call the real scraper
        scraper_result = await scrape_domain(
            domain_url=request.url,
            headless=True,
            max_products=10,  # Reasonable limit for analysis
            delay=1.0,
            min_jsonld_products=1  # At least 1 product required
        )
        
        print(f"✅ Scraper completed! Found {len(scraper_result.get('product_schemas', []))} product schemas")
        
        # Extract products from scraped data 
        products_data = scraper_result.get('product_schemas', [])
        
        if not products_data:
            print("⚠️  No product data found by scraper")
            return []
        
        # Step 2: Return raw scraper results for development
        print(f"🎉 SCRAPER COMPLETE: Returning raw scraper data for development")
        
        # Return the complete scraper result for debugging and development
        return {
            "scraped_products": products_data,
            "scraper_summary": scraper_result.get('crawler_summary', {}),
            "scraper_stats": {
                "products_found": len(products_data),
                "total_schemas": len(scraper_result.get('all_schemas', [])),
                "non_product_schemas": len(scraper_result.get('non_product_schemas', []))
            }
        }
        
        # COMMENTED OUT FOR SCRAPER DEVELOPMENT:
        # ========================================
        # # Step 2: Analyze with our existing ChatGPT pipeline
        # results = []
        # 
        # for i, product in enumerate(products_data, 1):
        #     try:
        #         print(f"🔍 Analyzing scraped product {i}/{len(products_data)}: {product.get('name', 'Unknown')}")
        #         
        #         # Validate required fields
        #         if not validate_schema_org_product(product):
        #             print(f"⚠️  Product {i} failed validation - skipping")
        #             continue
        #         
        #         # Analyze with ChatGPT (existing pipeline)
        #         print(f"🤖 Sending scraped product {i} to ChatGPT for analysis...")
        #         analysis = await chatgpt_model.analyze_product(product)
        #         print(f"✅ ChatGPT analysis complete for product {i} - Score: {analysis.get('overall_score', 'N/A')}/100")
        #         
        #         # Convert to response model
        #         response = ProductAnalysisResponse(**analysis)
        #         results.append(response)
        #         
        #     except Exception as e:
        #         print(f"❌ Error analyzing scraped product {i}: {str(e)}")
        #         error_response = ProductAnalysisResponse(
        #             overall_score=0,
        #             strengths=[],
        #             weaknesses=["Analysis failed"],
        #             improvements=[],
        #             seo_recommendations=[],
        #             missing_fields=[],
        #             conversion_tips=[],
        #             error=str(e)
        #         )
        #         results.append(error_response)
        # 
        # print(f"🎉 SCRAPE & ANALYSIS ARCHITECTURE COMPLETE: Returning {len(results)} analyses")
        # return results
        
    except Exception as e:
        print(f"💥 FATAL ERROR in scrape-and-analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scrape and analysis failed: {str(e)}")

@app.post("/scrape-only")
async def scrape_only(request: URLRequest):
    """Scraper development endpoint - returns raw scraper data only"""
    print(f"\n🔧 SCRAPER DEV MODE: Scraping {request.url}")
    
    try:
        # Import scraper
        from scraper.main import scrape_domain
        
        # Call the scraper with detailed logging
        print(f"🌐 Starting scraper for: {request.url}")
        scraper_result = await scrape_domain(
            domain_url=request.url,
            headless=True,
            max_products=10,
            delay=1.0,
            min_jsonld_products=1
        )
        
        # Extract data
        products_data = scraper_result.get('product_schemas', [])
        all_schemas = scraper_result.get('all_schemas', [])
        non_product_schemas = scraper_result.get('non_product_schemas', [])
        
        print(f"🎯 SCRAPER RESULTS:")
        print(f"   📦 Products found: {len(products_data)}")
        print(f"   📄 Total schemas: {len(all_schemas)}")
        print(f"   🔧 Non-product schemas: {len(non_product_schemas)}")
        
        # Return comprehensive scraper data for development
        return {
            "url": request.url,
            "status": "success",
            "products": products_data,
            "all_schemas": all_schemas, 
            "non_product_schemas": non_product_schemas,
            "crawler_summary": scraper_result.get('crawler_summary', {}),
            "extraction_result": scraper_result.get('extraction_result', {}),
            "error_aggregation": scraper_result.get('error_aggregation', {}),
            "stats": {
                "products_found": len(products_data),
                "total_schemas_found": len(all_schemas),
                "non_product_schemas_found": len(non_product_schemas)
            }
        }
        
    except Exception as e:
        print(f"💥 SCRAPER ERROR: {str(e)}")
        return {
            "url": request.url,
            "status": "error",
            "error": str(e),
            "products": [],
            "stats": {"products_found": 0, "total_schemas_found": 0}
        }

@app.post("/scrape-main-product")
async def scrape_main_product(request: URLRequest):
    """Smart endpoint that focuses on extracting the main product only, filtering out suggestions"""
    print(f"\n🎯 MAIN PRODUCT MODE: Analyzing {request.url}")
    
    try:
        # Import the focused main product scraper and context helper
        from scraper.main import scrape_main_product as _scraper_main_product
        from scraper.utils.product_context import scrape_product_context as _scrape_product_context
        
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
    
@app.post("/scrape-product-context")
async def scrape_product_context_endpoint(request: URLRequest):
    """Scraper endpoint: returns only HTML context and image URLs for a product page"""
    print(f"\n🔍 SCRAPING PRODUCT CONTEXT: {request.url}")
    try:
        from scraper.utils.product_context import scrape_product_context
        result = await scrape_product_context(request.url)
        # Log result for backend visibility
        images = result.get('images', {})
        print(f"[API] scrape-product-context images.urlMainimage: {images.get('urlMainimage')}")
        print(f"[API] scrape-product-context images.otherMainImages: {images.get('otherMainImages')}")
        html_ctx = result.get('relevantHtmlProductContext', '')
        html_preview = html_ctx if len(html_ctx) < 200 else html_ctx[:200] + '...'
        print(f"[API] scrape-product-context relevantHtmlProductContext: {html_preview}")
        return result
    except Exception as e:
        print(f"💥 PRODUCT CONTEXT SCRAPE ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Error scraping product context: {e}")

@app.options("/scrape-and-analyze")
async def scrape_options():
    """Handle CORS preflight for scrape-and-analyze endpoint"""
    print("🔧 OPTIONS request received for /scrape-and-analyze")
    return {"message": "OK"}

@app.options("/scrape-only")
async def scrape_only_options():
    """Handle CORS preflight for scrape-only endpoint"""
    print("🔧 OPTIONS request received for /scrape-only")
    return {"message": "OK"}

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