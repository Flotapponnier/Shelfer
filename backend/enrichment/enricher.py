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
    def enrich(input_data: dict) -> EnrichedProduct:
        # input_data: { 'json_ld_schema': {...}, 'html_contexts': { prop: {relevant_html_product_context: ...} } }
        original_schema = dict(input_data.get('json_ld_schema', {}))
        base_schema = dict(original_schema)  # copy for enrichment
        html_contexts = input_data.get('html_contexts', {})
        not_extracted = []
        for prop, ctx in html_contexts.items():
            context = PropertyContext(
                relevant_html_product_context=ctx.get('relevant_html_product_context'),
                productName=ctx.get('product_name'),
                productUrl=ctx.get('product_url')
            )
            prompt = ENRICHER_USER_PROMPT_TEMPLATE.format(
                property=prop,
                product_name=context.productName or "",
                product_url=context.productUrl or "",
                html=context.relevant_html_product_context or ""
            )
            llm_result = Enricher._call_llm_for_property(prompt)
            value = llm_result.get(prop) if isinstance(llm_result, dict) else llm_result
            if not value:
                not_extracted.append(prop)
            base_schema[prop] = value
        base_schema.setdefault("enriched", True)
        return EnrichedProduct(
            enriched_json_ld_schema=base_schema,
            original_json_ld_schema=original_schema,
            not_extracted_properties=not_extracted
        )
