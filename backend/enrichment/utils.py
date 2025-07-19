import re
import json

def clean_response(text: str) -> dict:
    """
    Clean and parse LLM response text into JSON.
    
    Args:
        text: Raw response text from LLM
        
    Returns:
        dict: Parsed JSON response
    """
    if text is None:
        return {}
    
    if not isinstance(text, str):
        return {}
    
    # Remove code block markers and strip whitespace
    cleaned_text = re.sub(r"```json|```", "", text).strip()
    
    if not cleaned_text:
        return {}
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        return {}
