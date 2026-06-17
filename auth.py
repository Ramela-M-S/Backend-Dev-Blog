from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings

from main import *
import hashlib
import secrets


db_dependency = Annotated[Session, Depends(get_db)]


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def generate_reset_token():
    return secrets.token_urlsafe(32)

def hash_reset_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the subject (user id) if valid."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
        db: db_dependency,
):
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token",headers={"WWW-Authenticate": "Bearer"},)

    user = db.query(Users).filter(Users.id==user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found",headers={"WWW-Authenticate": "Bearer"},)

    return user

CurrentUser= Annotated[Users, Depends(get_current_user)]
