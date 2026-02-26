# pii_masker.py

import re

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
PHONE_REGEX = r'\b\d{10}\b'
AADHAR_REGEX = r'\b\d{4}\s?\d{4}\s?\d{4}\b'

def mask_pii(text: str) -> str:
    if not text:
        return text

    text = re.sub(EMAIL_REGEX, "[EMAIL_MASKED]", text)
    text = re.sub(PHONE_REGEX, "[PHONE_MASKED]", text)
    text = re.sub(AADHAR_REGEX, "[AADHAR_MASKED]", text)

    return text