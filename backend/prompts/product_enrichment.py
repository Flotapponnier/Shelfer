# system + user prompt template
ENRICHER_SYSTEM_PROMPT = (
    "You are an expert product data extractor. "
    "Your task is to extract or infer specific schema.org properties "
    "for e-commerce products based on HTML context and product metadata."
)

ENRICHER_USER_PROMPT_TEMPLATE = """
Extract or infer the value for the property "{property}" for the product "{product_name}".
You can use the context provided:
- Product name: {product_name}
- Extra context: {html}

Instructions:
- Focus only on the property "{property}".
- If the value is not clearly stated, infer it.
- Format the response as a plain JSON object (not inside a code block).
- Do NOT wrap the JSON in triple backticks or any markdown formatting.
- Respond only with the JSON object and nothing else.
- If the {property} is not present return a json with empty string as value (key: "")
"""
