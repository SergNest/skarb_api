from datetime import datetime

import uvicorn
import httpx
import json

from redis import asyncio as aioredis
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Header, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from conf.config import settings
from src.schema import SType, SVendor, SZok

app = FastAPI()
security = HTTPBearer()

expected_token = settings.expected_token
security = HTTPBearer()


async def startup():
    redis = await aioredis.from_url(f"redis://{settings.redis_ip}:{settings.redis_port}", encoding="utf8",
                                    decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


@app.on_event("startup")
async def startup_event():
    await startup()


def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"token": token}


@app.get("/api/healthchecker")
def healthchecker():
    try:
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


@app.get("/")
async def root():
    return {"message": "Hello Skarb"}


@app.get("/dogovorhistory/{client_id}")
async def get_data_from_external_api(client_id: str, authorization: str = Header(None)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/history/dogovorhistory/{client_id}"
    if authorization != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url, timeout=500.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.get("/gettype/{search}/{category_id}", response_model=list[SType])
@cache(expire=240)
async def get_type_from_external_api(search: str,
                                     category_id: int,
                                     user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/gettype/{search}/{category_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.get("/getvendor/{search}", response_model=list[SVendor])
@cache(expire=240)
async def get_vendor_from_external_api(search: str, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/getvendor/{search}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.get("/checkzokbyphone", response_model=SZok)
@cache(expire=3600)
async def get_zok_by_phone(phone: str,
                           date: Optional[datetime] = None,
                           user: Optional[str] = Depends(authenticate)):

    central_base_api_url = (f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/checkzokbyphone"
                            f"?phone={phone}&date={date}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.post("/new_type")
async def get_data_from_external_api(data: dict, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/new_type/"

    headers = {
        "Content-Type": "application/json; charset=utf-8"  # Вказуємо, що дані передаються у форматі JSON
    }

    async with httpx.AsyncClient() as client:
        try:
            json_data = json.dumps(data)
            response = await client.post(central_base_api_url, data=json_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.post("/new_vendor")
async def get_data_from_external_api(data: dict, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/new_vendor/"

    headers = {
        "Content-Type": "application/json; charset=utf-8"  # Вказуємо, що дані передаються у форматі JSON
    }

    async with httpx.AsyncClient() as client:
        try:
            json_data = json.dumps(data)
            response = await client.post(central_base_api_url, data=json_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, port=55335)
