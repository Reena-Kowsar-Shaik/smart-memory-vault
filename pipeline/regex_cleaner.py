import re
from typing import Dict, List

REGEX_PATTERNS = {
    "dates": re.compile(
        r'\b(?:'
        r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|'
        r'\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|'
        r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
        r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
        r'\s+\d{1,2}(?:st|nd|rd|th)?(?:,)?\s+\d{4}|'
        r'\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
        r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}'
        r')\b',
        re.IGNORECASE
    ),
    "emails": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "urls": re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)'),
    "phone_numbers": re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'),
    "amounts": re.compile(r'(?:[\$€£¥₹]|USD|EUR|GBP|INR)\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|INR)\b')
}

def clean_text(raw_text: str) -> str:
    """Normalizes whitespace, fixes line wraps, and cleans text."""
    if not raw_text:
        return ""
    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'(?i)\bpage\s+\d+\s+(?:of|\/)\s+\d+\b', '', text)
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extracts dates, emails, URLs, phone numbers, and amounts using Regex."""
    entities: Dict[str, List[str]] = {}
    for key, pattern in REGEX_PATTERNS.items():
        matches = pattern.findall(text)
        seen = set()
        deduped = []
        for match in matches:
            m_clean = match.strip() if isinstance(match, str) else str(match).strip()
            if m_clean and m_clean.lower() not in seen:
                seen.add(m_clean.lower())
                deduped.append(m_clean)
        entities[key] = deduped
    return entities
