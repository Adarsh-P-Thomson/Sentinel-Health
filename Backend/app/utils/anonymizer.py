"""
Local PII/PHI Anonymizer
Uses regex patterns to remove personally identifiable information
NO AI/LLM calls - all processing is local and deterministic
"""
import re
from typing import Dict, List, Tuple
from datetime import datetime


class LocalAnonymizer:
    """
    Local anonymizer using regex patterns
    Removes PII/PHI without sending data to external APIs
    """
    
    def __init__(self):
        # Common first names (top 100 most common)
        self.common_names = {
            'james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
            'thomas', 'charles', 'mary', 'patricia', 'jennifer', 'linda', 'barbara', 'elizabeth',
            'susan', 'jessica', 'sarah', 'karen', 'nancy', 'lisa', 'betty', 'margaret', 'sandra',
            'ashley', 'kimberly', 'emily', 'donna', 'michelle', 'dorothy', 'carol', 'amanda',
            'melissa', 'deborah', 'stephanie', 'rebecca', 'sharon', 'laura', 'cynthia', 'kathleen',
            'amy', 'angela', 'shirley', 'anna', 'brenda', 'pamela', 'emma', 'nicole', 'helen',
            'samantha', 'katherine', 'christine', 'debra', 'rachel', 'catherine', 'carolyn', 'janet',
            'ruth', 'maria', 'heather', 'diane', 'virginia', 'julie', 'joyce', 'victoria', 'olivia',
            'kelly', 'christina', 'lauren', 'joan', 'evelyn', 'judith', 'megan', 'cheryl', 'andrea',
            'hannah', 'martha', 'jacqueline', 'frances', 'gloria', 'ann', 'teresa', 'kathryn', 'sara',
            'janice', 'jean', 'alice', 'madison', 'doris', 'abigail', 'julia', 'judy', 'grace', 'denise',
            'amber', 'danielle', 'brittany', 'rose', 'diana', 'brittany', 'natalie', 'sophia', 'alexis'
        }
        
        # US states and major cities
        self.locations = {
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut',
            'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa',
            'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',
            'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'hampshire',
            'jersey', 'mexico', 'york', 'carolina', 'dakota', 'ohio', 'oklahoma', 'oregon',
            'pennsylvania', 'rhode', 'tennessee', 'texas', 'utah', 'vermont', 'virginia',
            'washington', 'wisconsin', 'wyoming', 'chicago', 'houston', 'phoenix', 'philadelphia',
            'antonio', 'diego', 'dallas', 'jose', 'austin', 'jacksonville', 'francisco',
            'columbus', 'indianapolis', 'charlotte', 'seattle', 'denver', 'boston', 'detroit',
            'nashville', 'memphis', 'portland', 'vegas', 'louisville', 'baltimore', 'milwaukee',
            'albuquerque', 'tucson', 'fresno', 'sacramento', 'mesa', 'atlanta', 'omaha', 'miami',
            'oakland', 'tulsa', 'minneapolis', 'cleveland', 'wichita', 'arlington', 'raleigh'
        }
    
    def anonymize(self, text: str) -> Tuple[str, Dict]:
        """
        Anonymize text by removing PII/PHI
        
        Args:
            text: Raw text to anonymize
            
        Returns:
            Tuple of (anonymized_text, metadata)
            metadata contains: pii_detected, pii_types, pii_redaction_map, confidence
        """
        if not text:
            return text, {
                "pii_detected": False,
                "pii_types": [],
                "pii_redaction_map": {},
                "anonymizer_confidence": 1.0
            }
        
        anonymized = text
        pii_types = []
        redaction_map = {}
        
        # 1. Remove email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', anonymized)
        if emails:
            pii_types.append("email")
            for i, email in enumerate(emails):
                placeholder = f"[EMAIL_{i+1}]"
                redaction_map[placeholder] = email
                anonymized = anonymized.replace(email, placeholder)
        
        # 2. Remove phone numbers
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
            r'\+\d{1,3}\s?\d{1,14}',           # +1 234567890
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, anonymized)
            if phones:
                if "phone" not in pii_types:
                    pii_types.append("phone")
                for i, phone in enumerate(phones):
                    placeholder = f"[PHONE_{i+1}]"
                    redaction_map[placeholder] = phone
                    anonymized = anonymized.replace(phone, placeholder)
        
        # 3. Remove Social Security Numbers
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        ssns = re.findall(ssn_pattern, anonymized)
        if ssns:
            pii_types.append("ssn")
            for i, ssn in enumerate(ssns):
                placeholder = f"[SSN_{i+1}]"
                redaction_map[placeholder] = ssn
                anonymized = anonymized.replace(ssn, placeholder)
        
        # 4. Remove dates (potential DOB)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',    # 12/31/2020
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',    # 12-31-2020
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # January 1, 2020
        ]
        for pattern in date_patterns:
            dates = re.findall(pattern, anonymized, re.IGNORECASE)
            if dates:
                if "date" not in pii_types:
                    pii_types.append("date")
                for i, date in enumerate(dates):
                    placeholder = f"[DATE_{i+1}]"
                    redaction_map[placeholder] = date
                    anonymized = anonymized.replace(date, placeholder)
        
        # 5. Remove addresses (street addresses)
        # Pattern: number + street name + (St|Ave|Rd|Blvd|Dr|Ln|Way|Ct)
        address_pattern = r'\b\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b'
        addresses = re.findall(address_pattern, anonymized, re.IGNORECASE)
        if addresses:
            pii_types.append("address")
            for i, addr in enumerate(addresses):
                placeholder = f"[ADDRESS_{i+1}]"
                redaction_map[placeholder] = addr
                anonymized = anonymized.replace(addr, placeholder)
        
        # 6. Remove ZIP codes
        zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
        zips = re.findall(zip_pattern, anonymized)
        if zips:
            pii_types.append("zipcode")
            for i, zip_code in enumerate(zips):
                placeholder = f"[ZIP_{i+1}]"
                redaction_map[placeholder] = zip_code
                anonymized = anonymized.replace(zip_code, placeholder)
        
        # 7. Remove common names (case-insensitive)
        words = re.findall(r'\b[A-Z][a-z]+\b', anonymized)
        for word in words:
            if word.lower() in self.common_names:
                if "name" not in pii_types:
                    pii_types.append("name")
                placeholder = "[NAME]"
                # Only replace if it's a standalone word (not part of medical term)
                anonymized = re.sub(r'\b' + re.escape(word) + r'\b', placeholder, anonymized)
        
        # 8. Remove locations (cities, states)
        words = re.findall(r'\b[A-Z][a-z]+\b', anonymized)
        for word in words:
            if word.lower() in self.locations:
                if "location" not in pii_types:
                    pii_types.append("location")
                placeholder = "[LOCATION]"
                anonymized = re.sub(r'\b' + re.escape(word) + r'\b', placeholder, anonymized)
        
        # 9. Remove medical record numbers (MRN)
        mrn_pattern = r'\b(?:MRN|Medical Record|Patient ID)[\s:#]*([A-Z0-9-]+)\b'
        mrns = re.findall(mrn_pattern, anonymized, re.IGNORECASE)
        if mrns:
            pii_types.append("medical_record_number")
            for i, mrn in enumerate(mrns):
                placeholder = f"[MRN_{i+1}]"
                redaction_map[placeholder] = mrn
                anonymized = re.sub(mrn_pattern, placeholder, anonymized, flags=re.IGNORECASE)
        
        # 10. Remove insurance/policy numbers
        insurance_pattern = r'\b(?:Policy|Insurance|Member ID)[\s:#]*([A-Z0-9-]+)\b'
        insurance_ids = re.findall(insurance_pattern, anonymized, re.IGNORECASE)
        if insurance_ids:
            pii_types.append("insurance_id")
            for i, ins_id in enumerate(insurance_ids):
                placeholder = f"[INSURANCE_{i+1}]"
                redaction_map[placeholder] = ins_id
                anonymized = re.sub(insurance_pattern, placeholder, anonymized, flags=re.IGNORECASE)
        
        # Calculate confidence
        # High confidence if we found and removed PII
        # Lower confidence if text has many proper nouns we might have missed
        proper_nouns_remaining = len(re.findall(r'\b[A-Z][a-z]+\b', anonymized))
        confidence = 1.0 if proper_nouns_remaining < 3 else 0.85
        
        metadata = {
            "pii_detected": len(pii_types) > 0,
            "pii_types": list(set(pii_types)),  # Remove duplicates
            "pii_redaction_map": redaction_map,
            "anonymizer_confidence": confidence
        }
        
        return anonymized, metadata


# Global instance
anonymizer = LocalAnonymizer()


def anonymize_text(text: str) -> Tuple[str, Dict]:
    """
    Convenience function to anonymize text
    
    Args:
        text: Raw text to anonymize
        
    Returns:
        Tuple of (anonymized_text, metadata)
    """
    return anonymizer.anonymize(text)
