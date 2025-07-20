# scraper/jsonld_parser.py

import json
import re
from typing import Any, Dict, List, Optional

from ..utils.utils import logger


def parse_json_ld_scripts(script_contents: List[str]) -> List[Dict[str, Any]]:
    """Parses a list of raw JSON-LD script strings into a list of dictionary objects."""
    parsed_objects = []
    for i, content in enumerate(script_contents):
        try:
            cleaned_content = _clean_json_content(content)
            data = json.loads(cleaned_content)
            if isinstance(data, list):
                parsed_objects.extend(data)
            else:
                parsed_objects.append(data)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON-LD script #{i+1}: {e}")
            logger.debug(f"Problematic content snippet: {content[:200]}...")
        except Exception as e:
            logger.warning(f"Unexpected error parsing JSON-LD script #{i+1}: {e}")
    
    # Flatten nested structures to extract all individual objects
    flattened_objects = _flatten_nested_structures(parsed_objects)
    logger.info(f"Flattened {len(parsed_objects)} parsed objects to {len(flattened_objects)} individual schemas")
    
    return flattened_objects


def _flatten_nested_structures(objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts all schema objects from nested JSON-LD structures.
    
    This uses a comprehensive approach to find all objects with @type fields,
    regardless of their nesting level or structure.
    
    Args:
        objects: List of JSON-LD objects that may contain nested structures
        
    Returns:
        List of all individual schema objects found
    """
    all_schemas = []
    
    for obj in objects:
        if isinstance(obj, dict):
            # Extract all schema objects from this object (including the object itself)
            schemas = _extract_all_schemas(obj)
            all_schemas.extend(schemas)
    
    logger.debug(f"Extracted {len(all_schemas)} total schema objects from {len(objects)} input objects")
    return all_schemas


def _extract_all_schemas(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recursively extracts all schema objects from a JSON-LD object.
    
    This function traverses the entire object structure and extracts any object
    that has an @type or type field, which indicates it's a schema.org object.
    
    Args:
        obj: The JSON-LD object to search for schema objects
        
    Returns:
        List of all schema objects found (including the input object if it has @type or type)
    """
    schemas = []
    
    # If this object has @type or type, it's a schema object
    if isinstance(obj, dict) and ('@type' in obj or 'type' in obj):
        schemas.append(obj)
    
    # Recursively search all values in the object
    for key, value in obj.items():
        if isinstance(value, dict):
            # Recursively search nested objects
            nested_schemas = _extract_all_schemas(value)
            schemas.extend(nested_schemas)
        elif isinstance(value, list):
            # Search through arrays
            for item in value:
                if isinstance(item, dict):
                    nested_schemas = _extract_all_schemas(item)
                    schemas.extend(nested_schemas)
    
    return schemas


def _clean_json_content(content: str) -> str:
    """Cleans common HTML entities and whitespace from a JSON string."""
    content = content.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&apos;', "'")
    return re.sub(r'\s+', ' ', content).strip()

def _is_product_schema(obj: Dict[str, Any]) -> bool:
    """Checks if a JSON-LD object represents a product according to Schema.org."""
    if not isinstance(obj, dict):
        return False
    
    # Check for @type or type field - both are used in JSON-LD
    schema_type = obj.get('@type', '') or obj.get('type', '')
    if isinstance(schema_type, str):
        # Direct product type
        if schema_type.lower() in ['product', 'http://schema.org/product', 'https://schema.org/product']:
            type_field = '@type' if '@type' in obj else 'type'
            logger.debug(f"Found product schema by {type_field}: {schema_type}")
            return True
    elif isinstance(schema_type, list):
        # Multiple types - check if any are product
        for type_item in schema_type:
            if isinstance(type_item, str) and type_item.lower() in ['product', 'http://schema.org/product', 'https://schema.org/product']:
                type_field = '@type' if '@type' in obj else 'type'
                logger.debug(f"Found product schema by {type_field} in list: {type_item}")
                return True
    
    # Fallback: Check for product-specific fields that strongly indicate this is a product
    product_indicators = ['offers', 'sku', 'mpn', 'gtin13', 'gtin12', 'gtin8', 'ean', 'upc']
    has_product_fields = any(field in obj for field in product_indicators)
    
    # Also check if it has a name and offers (common product pattern)
    has_name_and_offers = 'name' in obj and 'offers' in obj
    
    is_product = has_product_fields or has_name_and_offers
    if is_product:
        logger.debug(f"Found product schema by indicators: name_and_offers={has_name_and_offers}, product_fields={has_product_fields}")
    
    return is_product

def deduplicate_and_select_best_schemas(objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates products and keeps the most comprehensive schema for each one."""
    if not objects:
        return []

    # Separate product and non-product schemas
    product_objects = [obj for obj in objects if _is_product_schema(obj)]
    non_product_objects = [obj for obj in objects if not _is_product_schema(obj)]
    
    logger.info(f"Found {len(product_objects)} product schemas and {len(non_product_objects)} non-product schemas")
    
    # Process product schemas (existing logic)
    deduplicated_products = _deduplicate_product_schemas(product_objects)
    
    # For non-product schemas, we'll keep them all for now (could add deduplication later if needed)
    # You might want to deduplicate non-products based on @type or other criteria
    deduplicated_non_products = _deduplicate_non_product_schemas(non_product_objects)
    
    # Combine both types
    all_schemas = deduplicated_products + deduplicated_non_products
    
    logger.info(f"Returning {len(deduplicated_products)} unique products and {len(deduplicated_non_products)} unique non-products (total: {len(all_schemas)})")
    return all_schemas

def _deduplicate_product_schemas(product_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates product schemas and keeps the most comprehensive one for each product."""
    if not product_objects:
        return []

    product_groups: Dict[str, List[Dict[str, Any]]] = {}
    for obj in product_objects:
        product_id = _get_product_identifier(obj)
        # If no identifier is found, treat the object as unique to avoid discarding it.
        unique_key = product_id if product_id else f"unique_{id(obj)}"
        
        if unique_key not in product_groups:
            product_groups[unique_key] = []
        product_groups[unique_key].append(obj)

    deduplicated_objects = []
    for product_id, group in product_groups.items():
        if len(group) == 1:
            deduplicated_objects.append(group[0])
        else:
            best_schema = _select_most_comprehensive_schema(group)
            deduplicated_objects.append(best_schema)
            logger.info(f"Selected best schema for product '{product_id}' from {len(group)} candidates.")
            
    logger.info(f"Deduplicated {len(product_objects)} product objects to {len(deduplicated_objects)} unique products.")
    return deduplicated_objects

def _deduplicate_non_product_schemas(non_product_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates non-product schemas based on @type and other identifying fields."""
    if not non_product_objects:
        return []

    # Group by @type for deduplication
    type_groups: Dict[str, List[Dict[str, Any]]] = {}
    for obj in non_product_objects:
        schema_type = obj.get('@type', '')
        if isinstance(schema_type, str):
            type_key = schema_type.lower()
        elif isinstance(schema_type, list):
            # Use the first type as the key
            type_key = schema_type[0].lower() if schema_type else 'unknown'
        else:
            type_key = 'unknown'
        
        if type_key not in type_groups:
            type_groups[type_key] = []
        type_groups[type_key].append(obj)

    deduplicated_objects = []
    for schema_type, group in type_groups.items():
        if len(group) == 1:
            deduplicated_objects.append(group[0])
        else:
            # For non-products, we could implement different deduplication logic
            # For now, just take the first one to avoid losing data
            deduplicated_objects.append(group[0])
            logger.info(f"Selected first schema for type '{schema_type}' from {len(group)} candidates.")
    
    logger.info(f"Deduplicated {len(non_product_objects)} non-product objects to {len(deduplicated_objects)} unique schemas.")
    return deduplicated_objects

def _get_product_identifier(obj: Dict[str, Any]) -> Optional[str]:
    """Extracts a unique product identifier from a JSON-LD object using a prioritized list of fields."""
    identifier_fields = [
        'sku', 'mpn', 'gtin13', 'gtin12', 'gtin8', 'ean', 'upc',
        'isbn', 'identifier', 'url', 'name'
    ]
    for field in identifier_fields:
        if value := obj.get(field):
            if isinstance(value, str) and value.strip():
                return f"{field}:{value.strip().lower()}"
    
    # Check within offers as a fallback
    if offers := obj.get('offers'):
        if isinstance(offers, dict): # Handle single offer object
             for field in identifier_fields:
                if value := offers.get(field):
                    if isinstance(value, str) and value.strip():
                        return f"offers.{field}:{value.strip().lower()}"
    return None

def _select_most_comprehensive_schema(schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Selects the best schema from a list by scoring its comprehensiveness."""
    return max(schemas, key=_calculate_schema_score)

def _calculate_schema_score(schema: Dict[str, Any]) -> int:
    """Calculates a comprehensiveness score based on field presence and content length."""
    score = len(json.dumps(schema, separators=(',', ':'))) # Base score for raw size

    # Bonus points for important top-level fields
    for field in ['name', 'description', 'image', 'offers', 'brand', 'aggregateRating', 'review']:
        if field in schema and schema[field]:
            score += 100
    
    # Bonus for nested fields
    if offers := schema.get('offers'):
        if isinstance(offers, dict):
            for field in ['price', 'priceCurrency', 'availability', 'itemCondition']:
                if field in offers and offers[field]:
                    score += 50
    
    if rating := schema.get('aggregateRating'):
        if isinstance(rating, dict):
            for field in ['ratingValue', 'reviewCount']:
                if field in rating and rating[field]:
                    score += 30
    return score