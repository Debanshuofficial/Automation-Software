from typing import List, Dict, Optional
from models.student import Student

class StudentManager:
    def __init__(self):
        self.students: Dict[str, Student] = {}
        
    def load_students(self, student_list: List[Student]):
        """Load a list of students into the manager, keyed by PEN ID."""
        self.students.clear()
        for student in student_list:
            self.students[student.pen_id] = student
            
    def get_student(self, pen_id: str) -> Optional[Student]:
        """Retrieve a student by PEN ID."""
        return self.students.get(pen_id)
        
    def has_student(self, pen_id: str) -> bool:
        """Check if a student exists by PEN ID."""
        return pen_id in self.students
        
    def get_all_students(self) -> List[Student]:
        """Return all loaded students."""
        return list(self.students.values())
        
    def count(self) -> int:
        """Return total number of loaded students."""
        return len(self.students)
