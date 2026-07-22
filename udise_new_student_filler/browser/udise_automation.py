import time
import re
from typing import Optional
from playwright.sync_api import Page
from utils.logger import AppLogger
from models.new_student import NewStudent

class UdiseNewStudentAutomation:
    def __init__(self, page: Page, logger: AppLogger):
        self.page = page
        self.logger = logger
        
    def scan_page_fields(self, student: NewStudent):
        """Scans the page for our known field mappings to identify which are present."""
        self.logger.info("Scanning page for known form fields...")
        found_fields = []
        try:
            self.page.wait_for_load_state('domcontentloaded')
            mappings = self.get_field_mappings(student)
            
            for pattern, value, input_type, field_name in mappings:
                # Look for text matching our pattern anywhere on the page
                loc = self.page.get_by_text(re.compile(pattern, re.IGNORECASE))
                
                # Also try placeholder
                loc_ph = self.page.get_by_placeholder(re.compile(pattern, re.IGNORECASE))
                
                if (loc.count() > 0 and loc.first.is_visible()) or (loc_ph.count() > 0 and loc_ph.first.is_visible()):
                    # Clean up the pattern string for display (remove regex artifacts)
                    display_name = pattern.replace('(', '').replace(')', '').replace('|', ' or ').replace('.*', ' ')
                    found_fields.append((display_name, field_name, value))
            
            if found_fields:
                self.logger.info(f"Found {len(found_fields)} known fields on the current page.")
            else:
                self.logger.info("No known form fields found on this page.")
                
            return found_fields
        except Exception as e:
            self.logger.error(f"Error scanning page fields: {e}")
            return []
            
    def get_field_mappings(self, student: NewStudent):
        """Returns a list of tuples: (Regex Pattern, Value, Input Type, Internal Field Name)"""
        if not student:
            # Return empty/dummy mappings if no student
            student = NewStudent()
            
        # Construct composite address
        address_parts = []
        if student.address:
            address_parts.append(student.address)
        if student.habitation_or_locality and student.habitation_or_locality.strip().lower() != student.address.strip().lower():
            address_parts.append(student.habitation_or_locality)
        if student.post_office:
            address_parts.append(student.post_office)
        if student.district:
            address_parts.append(student.district)
            
        composite_address = ", ".join(address_parts)
            
        return [
            # General Information
            (r"(Student's Name|Student Name)", student.student_name, "text", "student_name"),
            (r"Gender", student.gender, "select", "gender"),
            (r"Date of Birth", student.date_of_birth or student.dob, "text", "dob"),
            (r"Admission.*Class", student.admission_class, "select", "admission_class"),
            (r"Father's Name", student.father_name, "text", "father_name"),
            (r"Mother's Name", student.mother_name, "text", "mother_name"),
            (r"Guardian's Name", student.guardian_name, "text", "guardian_name"),
            (r"AADHAAR Number", student.aadhaar_no, "text", "aadhaar_no"),
            (r"Name.*AADHAAR", student.student_name, "text", "name_on_aadhaar"),
            (r"Social Category", student.social_category, "select", "social_category"),
            (r"Religion", student.religion, "select", "religion"),
            (r"Blood Group", student.blood_group, "select", "blood_group"),
            (r"Height", student.height_cms, "text", "height_cms"),
            (r"Weight", student.weight_kgs, "text", "weight_kgs"),
            (r"Identification Mark", student.identification_mark, "text", "identification_mark"),
            (r"Relationship.*Guardian", student.relationship_with_guardian, "select", "relationship_with_guardian"),
            (r"Annual.*Income", student.annual_family_income, "text", "annual_family_income"),
            (r"Qualification.*Father", student.qualification_father, "select", "qualification_father"),
            (r"Qualification.*Mother", student.qualification_mother, "select", "qualification_mother"),

            # Contact Information
            (r"Nationality", student.nationality, "select", "nationality"),
            (r"Country", student.country, "select", "country"),
            (r"State", student.state, "select", "state"),
            (r"Address", composite_address, "text", "address"),
            (r"Habitation|Locality", student.habitation_or_locality, "text", "habitation_or_locality"),
            (r"District", student.district, "select", "district"),
            (r"Block|Munc|Crop", student.block_munc_crop, "select", "block_munc_crop"),
            (r"Panchayat|Ward", student.panchayat_ward, "select", "panchayat_ward"),
            (r"Post office", student.post_office, "text", "post_office"),
            (r"Police Station", student.police_station, "text", "police_station"),
            (r"Pin Code|Pincode", student.pin_code or student.pincode, "text", "pincode"),
            (r"Mobile Number.*Parent", student.mobile_number_f, "text", "mobile_number"),
            (r"Alternate Mobile", student.mobile_number_m, "text", "alt_mobile_number"),
            (r"WhatsApp.*Mother", student.whatsapp_number_m, "text", "whatsapp_number_m"),
            (r"email", student.email_id or student.contact_email, "text", "email_id"),
            
            # Other Information
            (r"Birth Registration", student.birth_registration_number, "text", "birth_registration_number"),
            (r"BPL beneficiary", student.whether_bpl_beneficiary or student.bpl_beneficiary, "radio", "bpl_beneficiary"),
            (r"BPL No", student.bpl_no, "text", "bpl_no"),
            (r"Economically Weaker Section|EWS", student.economically_weaker_section, "radio", "economically_weaker_section"),
            (r"CWSN", student.whether_cwsn or student.cwsn, "radio", "cwsn"),
            (r"SLD|Type of Impairment", student.cwsn_type, "select", "cwsn_type"),
            (r"Out-of-School-Child", student.out_of_school_child, "radio", "out_of_school_child"),
            (r"mainstreamed", student.when_child_mainstreamed, "select", "when_child_mainstreamed"),
            (r"Health ID", student.health_id, "text", "health_id"),
        ]
        

    def fill_visible_fields(self, student: NewStudent) -> list:
        """
        Attempts to fill visible input fields on the current page based on the student data.
        Does not click any save or submit buttons.
        """
        self.logger.info("Attempting to fill visible fields...")
        try:
            mappings = self.get_field_mappings(student)
            filled_count = 0
            successfully_filled = []
            
            self.page.wait_for_load_state('domcontentloaded')

            for label_pattern, value, input_type, field_name in mappings:
                if not value:
                    continue # Skip empty data
                    
                if input_type in ["text", "select"]:
                    try:
                        # Fallback locators using regex text matching to find the label, then finding the next input
                        # MUST use visible=true so we don't accidentally anchor to a hidden tooltip at the top of the page
                        text_el = self.page.get_by_text(re.compile(label_pattern, re.IGNORECASE)).locator("visible=true").first
                        
                        locators = []
                        
                        # High priority: Exact known IDs from the UDISE+ Angular Portal
                        known_ids = {
                            "aadhaar_no": "#uuid",
                            "name_on_aadhaar": "#uuidName",
                            "dob": "#dob",
                            "gender": "#gender",
                        }
                        
                        if field_name in known_ids:
                            locators.append(self.page.locator(known_ids[field_name]))
                            
                        # High priority: Guess Angular formcontrolname based on our internal field name
                        locators.append(self.page.locator(f"[formcontrolname='{field_name}']"))
                        
                        if text_el.count() > 0:
                            # Use following:: traversal but strictly ignore any elements that have a disabled attribute in the DOM
                            if input_type == "text":
                                locators.append(text_el.locator("xpath=(.//input[not(@type='hidden') and not(@type='radio') and not(@type='checkbox') and not(@disabled)] | following::input[not(@type='hidden') and not(@type='radio') and not(@type='checkbox') and not(@disabled)])[1]"))
                            elif input_type == "select":
                                locators.append(text_el.locator("xpath=(.//select[not(@disabled)] | following::select[not(@disabled)])[1]"))
                        else:
                            self.logger.warning(f"Could not find VISIBLE text on page for: {label_pattern}")
                            
                        # Put standard locators at the end as a last resort
                        locators.append(self.page.get_by_placeholder(re.compile(label_pattern, re.IGNORECASE)))
                        locators.append(self.page.get_by_label(re.compile(label_pattern, re.IGNORECASE)))
                        
                        field_handled = False
                        for loc in locators:
                            if loc.count() > 0:
                                if loc.first.is_visible():
                                    # Skip if already filled
                                    current_val = loc.first.input_value() if input_type == "text" else loc.first.evaluate("el => el.value")
                                    el_html = loc.first.evaluate("el => el.outerHTML.substring(0, 150)")
                                    self.logger.info(f"[{label_pattern}] Matched input element: {el_html}")
                                    
                                    if current_val and str(current_val).strip() != "" and str(current_val) != "0":
                                        self.logger.info(f"Overwriting {label_pattern} (Old data: {current_val})")
                                        
                                    if input_type == "text":
                                        loc.first.fill(value, timeout=500)
                                    elif input_type == "select":
                                        # Find the exact option value using JS to handle partial matches like '1 - Male'
                                        option_val = loc.first.evaluate(f"""sel => {{
                                            for(let opt of sel.options) {{
                                                if(opt.text.toLowerCase().includes("{value.lower()}")) return opt.value;
                                            }}
                                            return null;
                                        }}""")
                                        if option_val:
                                            loc.first.select_option(value=option_val, timeout=500)
                                        else:
                                            loc.first.select_option(label=value, timeout=500) # Fallback
                                    filled_count += 1
                                    successfully_filled.append(field_name)
                                    self.logger.info(f"Filled {label_pattern} with {value}")
                                    field_handled = True
                                    break
                                else:
                                    self.logger.info(f"Locator for {label_pattern} found but is NOT visible.")
                        
                        if not field_handled:
                            self.logger.warning(f"Could not fill {label_pattern} - no visible and actionable input found.")
                            
                    except Exception as e:
                        self.logger.warning(f"Could not fill field matching {label_pattern}: {str(e)}")
                        
                elif input_type == "radio":
                    try:
                        label_el = self.page.get_by_text(re.compile(label_pattern, re.IGNORECASE)).locator("visible=true").first
                        if label_el.count() > 0:
                            # Look for the option label (e.g., 'Yes' or 'No')
                            val_label = self.page.locator("label").filter(has_text=re.compile(f"^{value}$", re.IGNORECASE))
                            
                            if val_label.count() > 0:
                                # The input might be inside the label, or it might be a preceding sibling
                                radio = val_label.first.locator("input[type='radio']")
                                if radio.count() == 0:
                                    # If not inside, look for a preceding sibling input (Angular Bootstrap style)
                                    radio = val_label.first.locator("xpath=preceding-sibling::input[@type='radio'][1]")
                                    
                                if radio.count() > 0:
                                    if not radio.first.is_checked():
                                        radio.first.check(timeout=500)
                                        filled_count += 1
                                        successfully_filled.append(field_name)
                                        self.logger.info(f"Checked radio {label_pattern} -> {value}")
                                else:
                                    self.logger.warning(f"Could not find radio input element for option: {value}")
                            else:
                                self.logger.warning(f"Could not find option label matching: {value}")
                    except Exception as e:
                        self.logger.warning(f"Could not check radio {label_pattern}: {str(e)}")

            self.logger.info(f"Successfully filled {filled_count} fields on the current page.")
            return successfully_filled
            
        except Exception as e:
            self.logger.error(f"Error while filling fields: {e}")
            return successfully_filled if 'successfully_filled' in locals() else []
