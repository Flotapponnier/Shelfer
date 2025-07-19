from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class PropertyContext(BaseModel):
    relevant_html_product_context: Optional[str]
    relevantJsonLdSchema: Optional[Dict[str, Any]] = None
    productName: Optional[str] = None
    productUrl: Optional[str] = None

class EnrichedProduct:
    def __init__(self, enriched_json_ld_schema: Dict[str, Any], original_json_ld_schema: Dict[str, Any], not_extracted_properties: List[str]):
        self.enriched_json_ld_schema = enriched_json_ld_schema
        self.original_json_ld_schema = original_json_ld_schema
        self.not_extracted_properties = not_extracted_properties
        self.finished = len(not_extracted_properties) == 0

    def __getitem__(self, item):
        return self.enriched_json_ld_schema[item]

    def __repr__(self):
        return (f"EnrichedProduct(enriched_json_ld_schema={self.enriched_json_ld_schema}, "
                f"original_json_ld_schema={self.original_json_ld_schema}, "
                f"finished={self.finished}, "
                f"not_extracted_properties={self.not_extracted_properties})")
