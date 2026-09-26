from datetime import datetime, timedelta, timezone
import hashlib, hmac, os
import jwt
from app.core.config import settings
ALGORITHM="HS256"

def hash_password(value:str)->str:
    salt=os.urandom(16)
    digest=hashlib.pbkdf2_hmac('sha256',value.encode(),salt,310000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"

def verify_password(value:str, stored:str)->bool:
    try:
        scheme,iterations,salt_hex,digest_hex=stored.split('$')
        if scheme!='pbkdf2_sha256': return False
        digest=hashlib.pbkdf2_hmac('sha256',value.encode(),bytes.fromhex(salt_hex),int(iterations))
        return hmac.compare_digest(digest.hex(),digest_hex)
    except Exception: return False

def create_token(subject:str)->str:
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({'sub':subject,'exp':exp},settings.secret_key,algorithm=ALGORITHM)

def decode_token(token:str)->str:
    data=jwt.decode(token,settings.secret_key,algorithms=[ALGORITHM]); return str(data['sub'])
