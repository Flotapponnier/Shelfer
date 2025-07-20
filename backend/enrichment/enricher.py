from typing import List, Optional, Dict, Any
from enrichment.models import PropertyContext, EnrichedProduct
from enrichment.utils import clean_response
from openai_client import OpenAIClient, AsyncOpenAIClient
from prompts.product_enrichment import ENRICHER_SYSTEM_PROMPT, ENRICHER_USER_PROMPT_TEMPLATE
import asyncio
import json

class AsyncEnricher:
    def __init__(self):
        self.openai_client = AsyncOpenAIClient()

    async def _call_llm_for_property(self, prompt: str) -> Any:
        raw = await self.openai_client.complete(
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

    async def enrich(self, product_metadata: dict, html_contexts: dict) -> EnrichedProduct:
        product_name = product_metadata.get('product_name', '')
        product_url = product_metadata.get('product_url', '')
        json_ld_schema = product_metadata.get('json_ld_schema')
        print("[ASYNC ENRICHER] Input json_ld_schema:")
        print(json.dumps(json_ld_schema, indent=2, ensure_ascii=False))
        original_schema = dict(json_ld_schema) if json_ld_schema else {}
        base_schema = dict(original_schema)
        not_extracted = []

        async def enrich_property(prop, ctx):
            context = PropertyContext(
                relevant_html_product_context=ctx.get('relevant_html_product_context', '')
            )
            prompt = ENRICHER_USER_PROMPT_TEMPLATE.format(
                property=prop,
                product_name=product_name,
                product_url=product_url,
                html=context.relevant_html_product_context
            )
            llm_result = await self._call_llm_for_property(prompt)
            value = llm_result.get(prop) if isinstance(llm_result, dict) else llm_result
            return prop, value

        tasks = [enrich_property(prop, ctx) for prop, ctx in html_contexts.items()]
        results = await asyncio.gather(*tasks)

        for prop, value in results:
            if not value:
                not_extracted.append(prop)
            else:
                base_schema[prop] = value

        base_schema.setdefault("enriched", True)
        return EnrichedProduct(
            enriched_json_ld_schema=base_schema,
            original_json_ld_schema=original_schema,
            not_extracted_properties=not_extracted
        )
