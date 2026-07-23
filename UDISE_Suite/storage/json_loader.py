import json
import os
from typing import List, Tuple
from pydantic import ValidationError
from models.student import Student

class JsonLoader:
    @staticmethod
    def load(filepath: str) -> Tuple[List[Student], List[str]]:
        """
        Loads the JSON file and parses it into Student objects.
        Returns a tuple of (List of valid students, List of error messages).
        """
        if not os.path.exists(filepath):
            return [], [f"File not found: {filepath}"]
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if "students" not in data or not isinstance(data["students"], list):
                return [], ["Invalid JSON format: missing 'students' array."]
                
            valid_students = []
            errors = []
            seen_pens = set()
            
            for index, item in enumerate(data["students"]):
                try:
                    student = Student(**item)
                    if student.pen_id in seen_pens:
                        errors.append(f"Row {index+1}: Duplicate PEN ID {student.pen_id}")
                        continue
                        
                    seen_pens.add(student.pen_id)
                    valid_students.append(student)
                except ValidationError as e:
                    errors.append(f"Row {index+1} validation error: {str(e)}")
                    
            return valid_students, errors
            
        except json.JSONDecodeError as e:
            return [], [f"JSON Parse Error: {str(e)}"]
        except Exception as e:
            return [], [f"Unexpected error loading JSON: {str(e)}"]
