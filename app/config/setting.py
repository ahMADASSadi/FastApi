from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
import asyncpg
from datetime import timedelta
from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, create_engine, SQLModel, select

from contextlib import contextmanager
from app.models.user_model import User


DATABASE_PASSWORD = '13801121'
DATABASE_USER = 'madassandd'
DATABASE_HOST = 'localhost'
DATABASE_NAME = 'faststore'
DATABASE_TYPE = 'postgresql'

DATABASE_URL = f"{
    DATABASE_TYPE}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"


def get_engine():
    ENGINE = create_engine(DATABASE_URL, echo=True)
    return ENGINE


async def create_database_if_not_exists():
    """
    Creates the database if it does not exist.
    """
    from sqlalchemy.engine import URL
    # Parse the database URL
    database_name = DATABASE_NAME
    connection = await asyncpg.connect(
        user=DATABASE_USER, password=DATABASE_PASSWORD, database='postgres', host=DATABASE_HOST
    )
    exists = await connection.fetchval(
        f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'"
    )
    if not exists:
        print(f"Database '{database_name}' does not exist. Creating it...")
        await connection.execute(f"CREATE DATABASE {database_name}")
        print(f"Database '{database_name}' created successfully.")
    await connection.close()


def create_db_and_tables():
    """
    Creates the database tables and relationships.
    """
    SQLModel.metadata.create_all(get_engine())


# @contextmanager
async def get_session():
    """
    Creates a new database session.
    """
    with Session(get_engine()) as session:
        yield session


SESSION_DEPENDENCY = Annotated[Session, Depends(get_session)]


OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='token')
SECRET_KEY = "834a7f566aad31a092f189b95db99bf5d4c42392a62724a1fec61814f8ebafae"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(days=1)
REFRESH_TOKEN_EXPIRE_MINUTES = timedelta(weeks=1)



def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


def verify_refresh_token(token: str):
    payload = verify_access_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    return payload


def get_current_user(token: str = Depends(OAUTH2_SCHEME), session: Session = Depends(get_session)):
    """
    Verifies the access token and returns the user data.
    """
    try:
        payload = verify_access_token(token)
        phone_number: str = payload.get("phone_number")
        if phone_number is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        # Query the user from the database
        query = select(User).where(User.phone_number == phone_number)
        user = session.exec(query).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",)


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        print(current_user.role)
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


ADMIN_USER = Depends(get_admin_user)
AUTHENTICATED_USER = Depends(get_current_user)


class Token:
    def __init__(self, expires_delta: timedelta = REFRESH_TOKEN_EXPIRE_MINUTES):
        self.expires_delta = expires_delta
    
    def create_access_token(self, data: dict):
        """
        Creates a new access token.

        Args:
            data (dict): get the data from the call to create the access token
            expires_delta (timedelta, optional): exiration time of the newly generated access token. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

        Raises:
            ValueError: if there is no access token

        Returns:
            str: the new access token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + self.expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    
    def create_refresh_token(self, data: dict):
        """
        Create a refresh token with an expiration date.

        Args:
            data (dict): Data to encode in the JWT.

        Returns:
            str: The encoded JWT refresh token.
        """
        expire = datetime.now(timezone.utc) + self.expires_delta
        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)