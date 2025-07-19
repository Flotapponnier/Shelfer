import os
import json
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/health")
async def health_check():
    print("💓 Health check requested")
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }