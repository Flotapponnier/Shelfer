# system + user prompt template
ENRICHER_SYSTEM_PROMPT = (
    "You are an expert product data extractor. "
    "Your task is to extract or infer specific schema.org properties "
    "for e-commerce products based on HTML context and product metadata."
)

ENRICHER_USER_PROMPT_TEMPLATE = """
Extract or infer the value for the property "{property}" for the product "{product_name}".
You can use the context provided
Context:
- Product name: {product_name}
- Extra context: {html}

Instructions:
- Focus only on the property "{property}".
- If the value is not clearly stated, infer it.
- Format the response as a JSON object with a single key: "{property}".
- The property either gets filled in or an empty string is returned.
Respond only with the JSON object.
"""
