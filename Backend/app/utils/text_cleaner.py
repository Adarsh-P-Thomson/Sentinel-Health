"""
Text Cleaning Utilities
Removes unwanted characters, formatting, and normalizes text for AI processing
"""
import re
from typing import Dict, List


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Removes:
    - Excessive newlines and whitespace
    - Special characters and formatting artifacts
    - URLs (but keeps the domain for context)
    - Email addresses (but keeps domain)
    - Phone numbers
    - Random character sequences
    - HTML entities
    - Markdown formatting
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text ready for AI processing
    """
    if not text:
        return ""
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    
    # Remove URLs but keep domain for context
    # Example: https://reddit.com/r/pharmacy/post123 -> [LINK: reddit.com]
    text = re.sub(
        r'https?://([a-zA-Z0-9.-]+)[^\s]*',
        r'[LINK: \1]',
        text
    )
    
    # Remove email addresses but keep domain
    # Example: john.doe@example.com -> [EMAIL: example.com]
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b',
        r'[EMAIL: \1]',
        text
    )
    
    # Remove phone numbers (various formats)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}', '[PHONE]', text)
    text = re.sub(r'\+\d{1,3}\s?\d{1,14}', '[PHONE]', text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_
    text = re.sub(r'~~([^~]+)~~', r'\1', text)      # ~~strikethrough~~
    text = re.sub(r'`([^`]+)`', r'\1', text)        # `code`
    
    # Remove Reddit/social media formatting
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url)
    text = re.sub(r'u/[A-Za-z0-9_-]+', '[USER]', text)     # u/username
    text = re.sub(r'r/[A-Za-z0-9_-]+', '[SUBREDDIT]', text) # r/subreddit
    text = re.sub(r'@[A-Za-z0-9_]+', '[MENTION]', text)    # @username
    text = re.sub(r'#[A-Za-z0-9_]+', '[HASHTAG]', text)    # #hashtag
    
    # Remove random character sequences (likely encoding errors)
    # Matches: ???, +++, \n\n\n, etc.
    text = re.sub(r'([^\w\s])\1{2,}', ' ', text)
    
    # Remove excessive whitespace and newlines
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
    text = re.sub(r'\s{2,}', ' ', text)     # Multiple spaces to single
    text = re.sub(r'\t+', ' ', text)        # Tabs to space
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    # Final cleanup
    text = text.strip()
    
    return text


def extract_metadata(text: str) -> Dict[str, List[str]]:
    """
    Extract metadata from text before cleaning
    
    Returns:
        Dictionary with extracted URLs, emails, usernames, etc.
    """
    metadata = {
        "urls": [],
        "emails": [],
        "phones": [],
        "usernames": [],
        "subreddits": [],
        "hashtags": []
    }
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s]+', text)
    metadata["urls"] = urls
    
    # Extract emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    metadata["emails"] = emails
    
    # Extract phone numbers
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
    metadata["phones"] = phones
    
    # Extract Reddit usernames
    usernames = re.findall(r'u/([A-Za-z0-9_-]+)', text)
    metadata["usernames"] = usernames
    
    # Extract subreddits
    subreddits = re.findall(r'r/([A-Za-z0-9_-]+)', text)
    metadata["subreddits"] = subreddits
    
    # Extract hashtags
    hashtags = re.findall(r'#([A-Za-z0-9_]+)', text)
    metadata["hashtags"] = hashtags
    
    return metadata


def normalize_medical_terms(text: str) -> str:
    """
    Normalize common medical term variations
    
    Examples:
    - "50mg" -> "50 mg"
    - "2x/day" -> "twice daily"
    """
    # Normalize dosage formats
    text = re.sub(r'(\d+)(mg|mcg|g|ml|cc)', r'\1 \2', text)
    
    # Normalize frequency
    replacements = {
        r'\b2x/day\b': 'twice daily',
        r'\b3x/day\b': 'three times daily',
        r'\b1x/day\b': 'once daily',
        r'\bqd\b': 'once daily',
        r'\bbid\b': 'twice daily',
        r'\btid\b': 'three times daily',
        r'\bqid\b': 'four times daily',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def is_meaningful_content(text: str, min_words: int = 5) -> bool:
    """
    Check if text contains meaningful content
    
    Args:
        text: Text to check
        min_words: Minimum number of words required
        
    Returns:
        True if text is meaningful, False otherwise
    """
    if not text or len(text.strip()) < 10:
        return False
    
    # Count actual words (not just whitespace or special chars)
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    
    return len(words) >= min_words
