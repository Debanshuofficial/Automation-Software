from typing import List, Tuple
from models.student import Student

class Validator:
    @staticmethod
    def validate_students_business_rules(students: List[Student]) -> Tuple[bool, List[str]]:
        """
        Validates business rules that go beyond schema constraints.
        E.g. attendance boundaries, marks boundaries.
        """
        errors = []
        warnings = []
        
        for student in students:
            if not (0 <= student.marks <= 100):
                warnings.append(f"PEN {student.pen_id}: Marks ({student.marks}) outside expected range (0-100).")
                
            if student.attendance < 0 or student.attendance > 365:
                warnings.append(f"PEN {student.pen_id}: Attendance ({student.attendance}) outside expected range (0-365).")
                
        return len(errors) == 0, errors + warnings
