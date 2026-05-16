import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "blackwhale-super-secret-key-2025")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def base64_url_encode(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64_url_decode(data: str) -> bytes:
    import base64
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)

def create_jwt_signature(header: dict, payload: dict) -> str:
    header_json = json.dumps(header, separators=(',', ':'))
    payload_json = json.dumps(payload, separators=(',', ':'))
    
    message = f"{base64_url_encode(header_json.encode())}.{base64_url_encode(payload_json.encode())}"
    signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    
    return base64_url_encode(signature)

def create_access_token(data: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(data.get("sub", "")),
        "email": data.get("email", ""),
        "role": data.get("role", "user"),
        "iat": int(time.time()),
        "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    
    header_encoded = base64_url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_encoded = base64_url_encode(json.dumps(payload, separators=(',', ':')).encode())
    signature = create_jwt_signature(header, payload)
    
    return f"{header_encoded}.{payload_encoded}.{signature}"

def decode_token(token: str) -> dict:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_encoded, payload_encoded, signature_encoded = parts
        
        expected_signature = create_jwt_signature(
            json.loads(base64_url_decode(header_encoded).decode()),
            json.loads(base64_url_decode(payload_encoded).decode())
        )
        
        if signature_encoded != expected_signature:
            return None
        
        payload = json.loads(base64_url_decode(payload_encoded).decode())
        
        if payload.get("exp", 0) < time.time():
            return None
        
        return payload
    except Exception:
        return None

def get_user_from_token(token: str, db_session):
    from database import User
    
    payload = decode_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        user_id = int(user_id)
    except:
        return None
    
    return db_session.query(User).filter(User.id == user_id).first()