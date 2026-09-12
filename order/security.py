import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

from .exceptions import InvalidTokenError

load_dotenv()
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password:str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)

def create_access_token(user_id):

    expire = datetime.now(timezone.utc) + timedelta(minutes =30)

    data = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(data,SECRET_KEY,ALGORITHM)

    expire = datetime.now(timezone.utc) + timedelta(minutes =30)
    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms = [ALGORITHM])

        user_id = int(payload["sub"])

        return user_id 

    except jwt.InvalidTokenError:
        raise InvalidTokenError("유효하지 않은 토큰")

