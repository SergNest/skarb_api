from fastapi import  HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from conf.config import settings

security = HTTPBearer()

expected_token = settings.expected_token

def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"token": token}