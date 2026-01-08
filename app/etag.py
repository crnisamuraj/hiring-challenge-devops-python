"""ETag utilities for optimistic concurrency control."""
import hashlib
import json
from typing import Any, Dict


def generate_etag(data: Dict[str, Any]) -> str:
    """Generate an ETag from server data.
    
    The ETag is a hash of the serializable fields, ensuring it changes
    when any field is modified.
    """
    # Convert datetime to ISO format string for hashing
    serializable = {}
    for key, value in data.items():
        if hasattr(value, 'isoformat'):
            serializable[key] = value.isoformat()
        else:
            serializable[key] = str(value) if value is not None else None
    
    content = json.dumps(serializable, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def etag_matches(etag: str, if_match: str | None) -> bool:
    """Check if the provided If-Match header matches the current ETag."""
    if if_match is None:
        return True  # No If-Match header means proceed
    
    # Handle weak ETags (W/"...")
    if_match = if_match.strip()
    if if_match.startswith('W/'):
        if_match = if_match[2:]
    if_match = if_match.strip('"')
    
    return etag == if_match


def etag_none_match(etag: str, if_none_match: str | None) -> bool:
    """Check if the ETag matches If-None-Match (return True if NOT modified)."""
    if if_none_match is None:
        return False  # No header means content is considered modified
    
    if_none_match = if_none_match.strip()
    if if_none_match.startswith('W/'):
        if_none_match = if_none_match[2:]
    if_none_match = if_none_match.strip('"')
    
    return etag == if_none_match
