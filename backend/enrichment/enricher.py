from enrichment.models import PropertyContext, EnrichedProduct
from enrichment.utils import clean_response
from enrichment.config import BASE_SCHEMA, ALLOWED_PROPERTIES
from openai_client import OpenAIClient
from prompts.product_enrichment import ENRICHER_SYSTEM_PROMPT, ENRICHER_USER_PROMPT_TEMPLATE

class Enricher:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or OpenAIClient()

    def _call_llm_for_property(self, prompt: str) -> dict:
        raw = self.llm_client.complete(
            ENRICHER_SYSTEM_PROMPT,
            prompt,
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=100,
        )
        try:
            return clean_response(raw)
        except Exception as e:
            return {"error": str(e)}

    def enrich_property(self, property_name: str, context: PropertyContext) -> dict:
        prompt = ENRICHER_USER_PROMPT_TEMPLATE.format(
            property=property_name,
            product_name=context.productName or "",
            product_url=context.productUrl or "",
            html=context.relevantHtmlProductContext or "",
        )
        return self._call_llm_for_property(prompt)

    def enrich(self, input_data: dict, properties: list = None) -> EnrichedProduct:
        if properties is None:
            properties = list(input_data.keys())
        schema = BASE_SCHEMA.copy()
        not_extracted = []

        for prop in properties:
            context = input_data.get(prop)
            if context:
                result = self.enrich_property(prop, context)
                value = result.get(prop)
                if not value:
                    not_extracted.append(prop)
                schema[prop] = value
        schema.setdefault("enriched", True)
        return EnrichedProduct(data=schema, not_extracted_properties=not_extracted)
