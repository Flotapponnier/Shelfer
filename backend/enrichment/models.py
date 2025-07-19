from typing import Optional, Dict, Any
from pydantic import BaseModel

class PropertyContext(BaseModel):
    relevantHtmlProductContext: Optional[str]
    relevantJsonLdSchema: Optional[Dict[str, Any]] = None
    productName: Optional[str] = None
    productUrl: Optional[str] = None

class EnrichedProduct:
    def __init__(self, data: Dict[str, Any], not_extracted_properties: List[str]):
        self.data = data
        self.not_extracted_properties = not_extracted_properties
        self.finished = len(not_extracted_properties) == 0

    def __getitem__(self, item):
        return self.data[item]

    def __repr__(self):
        return (f"EnrichedProduct(data={self.data}, "
                f"finished={self.finished}, "
                f"not_extracted_properties={self.not_extracted_properties})")
