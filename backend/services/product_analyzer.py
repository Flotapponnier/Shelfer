import json
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException
from models.chatgpt import ChatGPTModel
from schemas.product import ProductAnalysisResponse

class ProductAnalyzerService:
    def __init__(self):
        self.chatgpt_model = ChatGPTModel()
    
    async def process_uploaded_file(self, file: UploadFile) -> List[Dict[str, Any]]:
        """
        Process uploaded JSON file containing schema.org product data
        """
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
            
            # Ensure data is a list
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise HTTPException(status_code=400, detail="JSON must contain product data")
            
            return data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    async def analyze_products(self, products: List[Dict[str, Any]]) -> List[ProductAnalysisResponse]:
        """
        Analyze multiple products and return improvement suggestions
        """
        results = []
        
        for product in products:
            try:
                # Validate required fields
                if not self._validate_schema_org_product(product):
                    continue
                
                # Analyze with ChatGPT
                analysis = await self.chatgpt_model.analyze_product(product)
                
                # Convert to response model
                response = ProductAnalysisResponse(**analysis)
                results.append(response)
                
            except Exception as e:
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
        
        return results
    
    def _validate_schema_org_product(self, product: Dict[str, Any]) -> bool:
        """
        Validate that the product data follows schema.org structure
        """
        required_fields = ["@context", "@type", "name"]
        return all(field in product for field in required_fields)
    
    def _extract_product_summary(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key product information for analysis
        """
        return {
            "name": product.get("name", ""),
            "description": product.get("description", ""),
            "brand": product.get("brand", {}),
            "offers": product.get("offers", {}),
            "image": product.get("image", ""),
            "url": product.get("url", ""),
            "additional_properties": {k: v for k, v in product.items() 
                                   if k not in ["name", "description", "brand", "offers", "image", "url"]}
        }