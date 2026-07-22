import re
import time
from typing import List, Dict, Tuple
from playwright.sync_api import Page, Locator
from utils.logger import AppLogger
from models.student import Student

class UdiseAutomation:
    def __init__(self, page: Page, logger: AppLogger):
        self.page = page
        self.logger = logger
        self._should_stop = False
        
    def stop(self):
        self._should_stop = True

    def is_student_progression_page(self) -> bool:
        """Check if we are on the correct page."""
        try:
            # We look for some distinctive text on the page
            content = self.page.content()
            if "Student Progression" in content or "Progression Status" in content:
                self.logger.info("Student Progression Page Detected")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking page: {e}")
            return False

    def scan_page(self) -> List[Tuple[int, str, bool]]:
        """
        Scans the current page and extracts visible student PEN IDs and their completion status.
        Returns a list of tuples (row_index, pen_id, is_done).
        """
        self.logger.info("Scanning current webpage...")
        students_found = []
        try:
            # Wait for table body
            self.page.wait_for_selector("tbody tr", timeout=5000)
            rows = self.page.locator("tbody tr").all()
            
            for index, row in enumerate(rows):
                text = row.inner_text()
                # Looking for PEN ID in text, e.g., "PEN: 232380911"
                match = re.search(r'PEN:\s*(\d+)', text)
                if match:
                    pen_id = match.group(1).strip()
                    # Check if status is already "Done"
                    is_done = row.locator(".status-done").count() > 0 or "Done" in text
                    students_found.append((index, pen_id, is_done))
                    
            self.logger.info(f"Students Detected: {len(students_found)}")
            return students_found
        except Exception as e:
            self.logger.error(f"Error scanning page: {e}")
            return []

    def fill_student(self, row_index: int, pen_id: str, student_data: Student) -> bool:
        """
        Fills the fields for a specific student row based on the row index.
        """
        if self._should_stop:
            return False
            
        try:
            # Fetch the row
            row = self.page.locator("tbody tr").nth(row_index)
            
            # Selectors based on our mock layout. In reality, they might differ,
            # but we use typical Select/Input finding logic within the row.
            
            # 1. Progression Status
            prog_status_select = row.locator("select").filter(has_text=re.compile(r"Select.*Promoted.*", re.IGNORECASE)).first
            if prog_status_select.count() > 0:
                prog_status_select.select_option(label=student_data.progression_status)
            else:
                # Fallback to name/id pattern
                row.locator(f"select[name^='progression_status']").select_option(label=student_data.progression_status)

            # 2. Marks
            marks_input = row.locator("input[type='number']").first
            if marks_input.count() > 0:
                marks_input.fill(str(student_data.marks))
            else:
                row.locator(f"input[name^='marks']").fill(str(student_data.marks))

            # 3. Attendance
            attendance_input = row.locator("input[type='number']").nth(1)
            if attendance_input.count() > 0:
                attendance_input.fill(str(student_data.attendance))
            else:
                row.locator(f"input[name^='days']").fill(str(student_data.attendance))

            # 4. Schooling Status
            school_status_select = row.locator("select").filter(has_text=re.compile(r"Select.*Same School.*", re.IGNORECASE)).first
            if school_status_select.count() > 0:
                school_status_select.select_option(label=student_data.schooling_status)
            else:
                row.locator(f"select[name^='school_status']").select_option(label=student_data.schooling_status)

            # 5. Reason for Leaving (only fill if applicable)
            if student_data.reason_for_leaving:
                reason_select = row.locator(f"select[name^='reason']")
                if reason_select.count() > 0:
                    reason_select.select_option(label=student_data.reason_for_leaving)

            # 6. Section
            section_select = row.locator(f"select[name^='section']")
            if section_select.count() > 0:
                section_select.select_option(label=student_data.section)

            # Trigger change events if necessary
            # Playwright select_option and fill automatically trigger change/input events.
            
            self.logger.info(f"Filled PEN {pen_id}")
            time.sleep(0.1) # Small intelligent delay
            return True
            
        except Exception as e:
            self.logger.error(f"Unable to locate or fill fields for PEN {pen_id}: {e}")
            return False
