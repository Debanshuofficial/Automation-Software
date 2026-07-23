from dataclasses import dataclass, field
from typing import Optional

@dataclass
class NewStudent:
    # General Information
    student_name: str = ""
    gender: str = ""
    date_of_birth: str = "" # maps to dob
    admission_class: str = ""
    father_name: str = ""
    mother_name: str = ""
    guardian_name: str = ""
    aadhaar_no: str = ""
    social_category: str = ""
    religion: str = ""
    blood_group: str = ""
    height_cms: str = ""
    weight_kgs: str = ""
    identification_mark: str = ""
    relationship_with_guardian: str = ""
    annual_family_income: str = ""
    qualification_father: str = ""
    qualification_mother: str = ""
    
    # Contact Information
    nationality: str = ""
    country: str = ""
    state: str = ""
    address: str = ""
    habitation_or_locality: str = ""
    district: str = ""
    block_munc_crop: str = ""
    panchayat_ward: str = ""
    post_office: str = ""
    police_station: str = ""
    pin_code: str = ""
    mobile_number_f: str = ""
    mobile_number_m: str = ""
    whatsapp_number_m: str = ""
    email_id: str = ""
    
    # Other Information
    birth_registration_number: str = ""
    whether_bpl_beneficiary: str = ""
    bpl_no: str = ""
    economically_weaker_section: str = ""
    whether_cwsn: str = ""
    cwsn_type: str = ""
    out_of_school_child: str = ""
    when_child_mainstreamed: str = ""
    health_id: str = ""
    
    # Legacy / Compatibility fields that might still be used by code
    dob: str = ""
    state_code: str = ""
    name_on_aadhaar: str = ""
    admission_date: str = ""
    mobile_number: str = ""
    alt_mobile_number: str = ""
    cwsn: str = ""
    pincode: str = ""
    contact_email: str = ""
    mother_tongue: str = ""
    minority_group: str = ""
    bpl_beneficiary: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'NewStudent':
        return cls(**{
            k: v for k, v in data.items() 
            if k in cls.__dataclass_fields__
        })
