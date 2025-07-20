from typing import List, Optional, Dict, Any
from enrichment.models import PropertyContext
from enrichment.utils import clean_response
from openai_client import AsyncOpenAIClient
from prompts.product_enrichment import ENRICHER_SYSTEM_PROMPT, ENRICHER_USER_PROMPT_TEMPLATE
import asyncio
import json
import os

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

    async def enrich(self, product_metadata: dict, html_contexts: dict) -> dict:
        print("\n[Enricher] Product Metadata Received:")
        print(json.dumps(product_metadata, indent=2, ensure_ascii=False))
        product_name = product_metadata.get('product_name', '')
        product_url = product_metadata.get('product_url', '')
        json_ld_schema = product_metadata.get('json_ld_schema')
        # Patch: handle both dict and list for json_ld_schema
        if isinstance(json_ld_schema, dict):
            original_schema = dict(json_ld_schema)
        elif isinstance(json_ld_schema, list) and json_ld_schema and isinstance(json_ld_schema[0], dict):
            original_schema = dict(json_ld_schema[0])
        else:
            original_schema = {}
        enriched_json_schema = dict(original_schema)

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

        # Write results to a file for inspection
        def safe_serialize(obj):
            try:
                json.dumps(obj)
                return obj
            except Exception:
                return str(obj)
        serializable_results = [
            (prop, safe_serialize(value)) for prop, value in results
        ]
        results_path = os.path.join(os.path.dirname(__file__), 'enrichment_results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)

        not_extracted_properties = []
        for prop, value in results:
            if value is not None and value != "":
                enriched_json_schema[prop] = value
            else:
                not_extracted_properties.append(prop)

        enriched_json_schema.setdefault("enriched", True)
        return enriched_json_schema, not_extracted_properties
