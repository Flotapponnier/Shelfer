import re
import json

def clean_response(text: str) -> dict:
    text = re.sub(r"```json|```", "", text).strip()
    return json.loads(text)
