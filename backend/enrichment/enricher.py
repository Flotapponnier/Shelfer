from typing import List, Optional, Dict, Any
from enrichment.models import PropertyContext, EnrichedProduct
from enrichment.utils import clean_response
from openai_client import OpenAIClient
from prompts.product_enrichment import ENRICHER_SYSTEM_PROMPT, ENRICHER_USER_PROMPT_TEMPLATE


class Enricher:
    openai_client = OpenAIClient()

    @staticmethod
    def _call_llm_for_property(prompt: str) -> Any:
        raw = Enricher.openai_client.complete(
            ENRICHER_SYSTEM_PROMPT,
            prompt,
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=100
        )
        try:
            return clean_response(raw)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def enrich(
        product_metadata: dict, 
        html_contexts: dict
    ) -> EnrichedProduct:
        """
        Enrich product schema using LLM with clean, separated inputs.
        
        Args:
            product_metadata: {
                'product_name': str,
                'product_url': str, 
                'json_ld_schema': dict (optional existing schema)
            }
            html_contexts: {
                'offers.price': {'relevant_html_product_context': '<span>$29.99</span>'},
                'material': {'relevant_html_product_context': '<div>Cotton</div>'},
                ...
            }
            
        Returns:
            EnrichedProduct with enriched schema and metadata
        """
        # Extract product metadata
        product_name = product_metadata.get('product_name', '')
        product_url = product_metadata.get('product_url', '')
        
        # Handle json_ld_schema safely (can be None)
        json_ld_schema = product_metadata.get('json_ld_schema')
        original_schema = dict(json_ld_schema) if json_ld_schema else {}
        
        # Start with original schema as base for enrichment
        base_schema = dict(original_schema)
        not_extracted = []
        
        # Process each property context
        for prop, ctx in html_contexts.items():
            context = PropertyContext(
                relevant_html_product_context=ctx.get('relevant_html_product_context', '')
            )
            
            prompt = ENRICHER_USER_PROMPT_TEMPLATE.format(
                property=prop,
                product_name=product_name,
                product_url=product_url,
                html=context.relevant_html_product_context
            )
            
            llm_result = Enricher._call_llm_for_property(prompt)
            value = llm_result.get(prop) if isinstance(llm_result, dict) else llm_result
            
            if not value:
                not_extracted.append(prop)
            else:
                base_schema[prop] = value
        
        # Add enrichment marker
        base_schema.setdefault("enriched", True)
        
        return EnrichedProduct(
            enriched_json_ld_schema=base_schema,
            original_json_ld_schema=original_schema,
            not_extracted_properties=not_extracted
        )
