from jose import jwt
from typing import Dict, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose.exceptions import JWTError
import uuid
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"

def create_jwt_token(data: Dict, expires_delta: timedelta = timedelta(minutes=30)) -> Tuple[str, str]:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti

def decode_jwt_token(token: str) -> Dict:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
