import json
import tempfile
import os
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException

class FileUtils:
    
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> str:
        """
        Save uploaded file to temporary location and return path
        """
        try:
            # Create temporary file
            suffix = os.path.splitext(file.filename)[1] if file.filename else '.json'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            
            # Write content to temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """
        Clean up temporary file
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # Ignore cleanup errors
    
    @staticmethod
    def validate_json_structure(data: Any) -> bool:
        """
        Validate that the JSON has the expected structure
        """
        if isinstance(data, dict):
            return "@context" in data and "@type" in data
        elif isinstance(data, list):
            return all(isinstance(item, dict) and "@context" in item and "@type" in item for item in data)
        return False
    
    @staticmethod
    def extract_product_count(data: Any) -> int:
        """
        Count the number of products in the data
        """
        if isinstance(data, dict):
            return 1
        elif isinstance(data, list):
            return len(data)
        return 0