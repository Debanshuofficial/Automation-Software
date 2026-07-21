from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    pen_id: str = Field(description="PEN ID of the student")
    marks: int = Field(description="Marks in Percentage")
    attendance: int = Field(description="No. of Days School attended")
    progression_status: str = Field(description="Status of progression e.g., Promoted/Passed")
    schooling_status: str = Field(description="Schooling status for next year")
    reason_for_leaving: Optional[str] = Field(default="", description="Reason for leaving, if applicable")
    section: str = Field(description="Section assigned for next year")
