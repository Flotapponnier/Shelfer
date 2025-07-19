import os
from typing import Dict, Any, List, Optional
import openai
from dotenv import load_dotenv
from prompts.product_analysis import (
    PRODUCT_ANALYSIS_SYSTEM_PROMPT,
    PRODUCT_COMPARISON_PROMPT,
    SCHEMA_VALIDATION_PROMPT
)

load_dotenv()

class ChatGPTModel:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    async def analyze_product(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze schema.org product data and suggest improvements
        """
        try:
            system_prompt = self._get_product_analysis_prompt()
            user_content = f"Product Data to Analyze:\n{schema_data}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_analysis_response(content)
            
        except Exception as e:
            raise Exception(f"Error analyzing product: {str(e)}")
    
    async def compare_products(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple products and provide competitive analysis
        """
        try:
            user_content = f"Products to Compare:\n{products_data}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PRODUCT_COMPARISON_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_analysis_response(content)
            
        except Exception as e:
            raise Exception(f"Error comparing products: {str(e)}")

    async def validate_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate schema.org markup and suggest improvements
        """
        try:
            user_content = f"Schema.org Product Data to Validate:\n{schema_data}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SCHEMA_VALIDATION_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            return self._parse_analysis_response(content)
            
        except Exception as e:
            raise Exception(f"Error validating schema: {str(e)}")

    def _get_product_analysis_prompt(self) -> str:
        """
        System prompt for product analysis
        """
        return PRODUCT_ANALYSIS_SYSTEM_PROMPT

    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """
        Parse the ChatGPT response into structured data
        """
        try:
            import json
            # Try to extract JSON from the response
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create structured response from text
                return {
                    "overall_score": 75,
                    "analysis": content,
                    "strengths": [],
                    "weaknesses": [],
                    "improvements": [],
                    "seo_recommendations": [],
                    "missing_fields": [],
                    "conversion_tips": []
                }
        except Exception:
            return {
                "overall_score": 75,
                "analysis": content,
                "error": "Could not parse structured response"
            }