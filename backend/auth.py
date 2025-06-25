# auth.py
from fastapi import HTTPException
from typing import Dict

# Simple token cache (in-memory, for demo)
token_cache: Dict[str, str] = {}

def get_access_token():
    token = token_cache.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated. Please go to /login.")
    return token
