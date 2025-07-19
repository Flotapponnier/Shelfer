"""
System and user prompts for extracting relevant HTML contexts for schema.org properties
"""

HTML_EXTRACTION_SYSTEM_PROMPT = """You are an expert HTML analyzer specialized in extracting relevant product information. Your task is to identify and extract the specific HTML segments that contain information relevant to a given schema.org product property.

Given a full product HTML page and a specific schema.org property, you must:
1. Analyze the HTML to find sections that contain information relevant to the property
2. Extract ONLY the most relevant HTML chunks (not the entire page)
3. Focus on extracting content-rich elements while preserving structure
4. Remove unnecessary nested elements that don't add value
5. Prioritize product-specific content over navigation, headers, footers, etc.

Return only the relevant HTML chunks as a string. If no relevant information is found, return an empty string.

Be precise and focused - extract only what's needed for the specific property."""

HTML_EXTRACTION_USER_PROMPT_TEMPLATE = """
Property to extract: "{property}"

Property description for context:
{property_description}

Full Product HTML:
{product_html}

Extract the most relevant HTML chunks that contain information for the property "{property}". Return only the HTML content as a string, no additional formatting or explanation.
"""

# Property descriptions to provide context for extraction
PROPERTY_DESCRIPTIONS = {
    "offers.price": "The selling price of the product, including any sale prices, discounts, or price ranges",
    "offers.priceCurrency": "The currency used for the product price (e.g., USD, EUR, GBP)",
    "offers.availability": "The availability status of the product (in stock, out of stock, limited availability, etc.)",
    "description": "The product description, features, specifications, and detailed information about the product",
    "brand": "The brand or manufacturer name of the product",
    "offers.itemCondition": "The condition of the product (new, used, refurbished, damaged, etc.)",
    "color": "The color or colors available for the product",
    "material": "The material the product is made from (fabric, metal, plastic, wood, etc.)",
    "aggregateRating": "Customer ratings, review scores, star ratings, and rating summaries",
    "review": "Customer reviews, testimonials, and user feedback about the product",
    "category": "The product category, type, or classification (electronics, clothing, home goods, etc.)",
    "keywords": "Keywords, tags, or descriptive terms associated with the product",
    "manufacturer": "The manufacturer or company that produces the product",
    "size": "Size information, dimensions, measurements, or size charts for the product",
    "audience": "Target audience, age group, or intended users for the product",
    "additionalType": "Additional product types, subcategories, or classification details",
    "hasMerchantReturnPolicy": "Return policy, exchange policy, warranty information, or return terms",
    "negativeNotes": "Negative aspects, warnings, limitations, or cautions about the product",
    "positiveNotes": "Positive highlights, benefits, special features, or selling points of the product",
    "nsn": "NATO Stock Number, part number, SKU, or unique product identifier",
    "countryOfLastProcessing": "Country of origin, manufacturing location, or where the product was processed",
    "isFamilyFriendly": "Whether the product is appropriate for children or families, age restrictions"
} 