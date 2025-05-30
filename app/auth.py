from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug("Verifying password")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    logger.debug("Hashing password")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(f"Created access token for subject: {data.get('sub')}")
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token verification failed: Subject claim missing")
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        logger.warning("Token verification failed: JWTError")
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        logger.warning(f"Token verification failed: User not found for email: {token_data.email}")
        raise credentials_exception
    logger.debug(f"Successfully retrieved user {user.email} from token")
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    logger.debug(f"Checking if user {current_user.email} is active")
    # Assuming all users are active for this basic example
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    logger.debug(f"User {current_user.email} is active")
    return current_user 