from passlib.context import CryptContext
from jose import jwt
import datetime
from travelhub_common.config import BaseAppSettings
from travelhub_common.security import RoleEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, settings: BaseAppSettings):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})
    
    if not settings.jwt_private_key:
        raise ValueError("JWT private key not configured")
        
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_private_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt
