from datetime import datetime, timedelta, UTC
from typing import Optional
from aiocache import cached

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
import logging

from src.database.db import get_db
from src.database.models import UserRole, User
from src.conf.config import settings
from src.services.users import UserService
from src.utils import HTTPBadRequestException

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(payload: dict, expires_delta: Optional[int] = None):
    """
    Create an access token

    Args:
        payload (dict): provided data for payload.
        expires_delta (int, Optional): time delta

    Returns:
        str
    """

    payload_data = payload.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(
            seconds=int(settings.JWT_EXPIRATION_SECONDS)
        )
    payload_data.update({"exp": expire})
    encoded = jwt.encode(
        payload_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded


def create_token(payload: dict):
    """
    Create a token with provided payload

    Args:
        payload (dict): provided data for payload.

    Returns:
        str
    """

    to_encode = payload.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def cached_key(func, args, kwargs):
    return f"username {args[0]}"


@cached(ttl=180, key_builder=cached_key)  # 3 minutes
async def get_current_user_from_db(username: str, db: AsyncSession) -> User | None:
    """
    Return a current user from either database or a cache, save id redis by a username

    Args:
        username (str): username for searching.
        db (AsyncSession): instance of AsyncSession

    Returns:
        User
    """
    logger.info(f'Search "{username}" in database.')
    user_service = UserService(db)
    return await user_service.get_user_by_username(username)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Return a current user

    Args:
        token (str): access token.
        db (AsyncSession): instance of AsyncSession

    Returns:
        User
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_current_user_from_db(username, db)
    if user is None:
        raise credentials_exception

    return user


def get_current_user_admin(current_user: User = Depends(get_current_user)):
    """
    Get current user if a role is Admin

    Args:
        current_user (User): Injected instance of a User.

    Returns:
        An Admin User
    """

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permission Denided")
    return current_user


async def get_email_from_token(token: str):
    """
    Return email from a provided token

    Args:
        token (str): token.

    Returns:
        str
    """

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError:
        raise HTTPBadRequestException("Invalid or expired token")
