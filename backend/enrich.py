from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import importlib
from prompts.product_enrichment import ENRICHER_SYSTEM_PROMPT, ENRICHER_USER_PROMPT_TEMPLATE
import openai
import dotenv
import re
import json

dotenv.load_dotenv()


class PropertyContext(BaseModel):
    relevantHtmlProductContext: Optional[str]
    relevantJsonLdSchema: Optional[Dict[str, Any]] = None
    productName: Optional[str] = None
    productUrl: Optional[str] = None

ProductEnrichmentInput = Dict[str, PropertyContext]
EnrichedProduct = Dict[str, Any]

ALLOWED_PROPERTIES = [
    "color",
    "keywords",
    "brand",
]

def clean_response(text):
    # remove triple backticks and optional 'json'
    text = re.sub(r"```json|```", "", text).strip()
    return json.loads(text)

# Import the prompt from product_enrichment.py
class Enricher:
    @staticmethod
    def _call_llm_for_property(prompt: str) -> Any:
        try:
            client = openai.OpenAI()  # This uses the OPENAI_API_KEY env variable
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": ENRICHER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=100
            )
            raw = response.choices[0].message.content.strip()
            return clean_response(raw)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def enrich_property(property_name: str, context: PropertyContext) -> EnrichedProduct:
        prompt = ENRICHER_USER_PROMPT_TEMPLATE.format(
            property=property_name,
            product_name=context.productName or "",
            product_url=context.productUrl or "",
            html=context.relevantHtmlProductContext or ""
        )
        llm_result = Enricher._call_llm_for_property(prompt)
        return llm_result

    @staticmethod
    def enrich(input_data: ProductEnrichmentInput, properties: list = None) -> EnrichedProduct:
        if properties is None:
            properties = list(input_data.keys())
        base_schema = {
            "@context": "https://schema.org/",
            "@type": "Product"
        }
        for prop in properties:
            context = input_data.get(prop)
            if context:
                base_schema[prop] = Enricher.enrich_property(prop, context)
        base_schema.setdefault("enriched", True)
        return base_schema