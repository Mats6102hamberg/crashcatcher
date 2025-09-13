import os
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "devkey")  # byt i compose

def require_api_key(x_api_key: str | None = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Not authenticated")
