from jose import jwt
from typing import Dict
from datetime import datetime
from fastapi import HTTPException
from jose.exceptions import JWTError
import os


# In prod, keep safe
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"

def create_jwt_token(data: Dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str) -> Dict:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ Token successfully decoded:", decoded)
        return decoded
    except JWTError as e:
        print("❌ JWT decode failed:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
