import json
import os
from typing import Tuple, Optional
from models.new_student import NewStudent

class JsonLoader:
    @staticmethod
    def load(filepath: str) -> Tuple[Optional[NewStudent], list]:
        """Loads a single student from a JSON file, flattening nested sections."""
        if not os.path.exists(filepath):
            return None, ["File does not exist."]
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Flatten the JSON structure from Gemini
            flat_data = {}
            if 'general_information' in data:
                flat_data.update(data['general_information'])
            if 'contact_information' in data:
                flat_data.update(data['contact_information'])
            if 'other_information' in data:
                flat_data.update(data['other_information'])
                
            # Also include any top-level keys just in case it's the old format
            for k, v in data.items():
                if not isinstance(v, dict):
                    flat_data[k] = v
                    
            student = NewStudent.from_dict(flat_data)
            return student, []
            
        except json.JSONDecodeError as e:
            return None, [f"Invalid JSON format: {e}"]
        except Exception as e:
            return None, [f"Error reading file: {e}"]
