import datetime

import aiofiles
import uvicorn
import httpx
import json

from redis import asyncio as aioredis
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Header, Depends, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from starlette.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from auth import authenticate, expected_token, create_access_token, verify_token
from conf.config import settings
from src.schema import LoginRequest, SType, SVendor

from elombard.zok import router as zok
from elombard.new_offer import router as offer
from elombard.general_purpose import router as general
from notifications.telegram_send import router as telegram_send
from work_with_foto.photo_route import router as photo
from sun_flower.sunflower_route import router as sf
from utils.logger_config import logger


BLOCKED_PATHS = ["/.env", "/.git", "/.config", "/config.json", "/sslvpn_logon.shtml"]
MAX_ATTEMPTS = 3
BLOCK_SECONDS = 300

app = FastAPI()

# app.mount("/main", StaticFiles(directory="dist", html=True), name="static")


async def log_blocked_ip(ip_address):
    async with aiofiles.open("blocked_ips.txt", "a") as f:
        await f.write(f"{ip_address} - {datetime.datetime.now()}\n")


@app.middleware("http")
async def block_paths_middleware(request: Request, call_next):
    if request.url.path in BLOCKED_PATHS:
        logger.warning(f"Blocked access to {request.url.path} from {request.client.host}")

        # Запис IP-адреси у файл
        await log_blocked_ip(request.client.host)

        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden path"}
        )
    return await call_next(request)


app.include_router(zok)
app.include_router(telegram_send)
app.include_router(photo)
app.include_router(sf)
app.include_router(offer)
app.include_router(general)

async def startup():
    redis = await aioredis.from_url(f"redis://{settings.redis_ip}:{settings.redis_port}", encoding="utf8",
                                    decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


@app.on_event("startup")
async def startup_event():
    await startup()


@app.get("/api/healthchecker")
async def healthchecker():
    try:
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")

@app.post("/auth/login")
async def login(data: LoginRequest, request: Request):
    ip = request.client.host
    key = f"login_attempts:{data.username}:{ip}"

    redis = FastAPICache.get_backend().redis
    attempts = await redis.get(key)
    attempts = int(attempts) if attempts else 0

    if attempts >= MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="🔒 Too many attempts. Try later.")

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"http://{settings.ip_central}:{settings.port_central}/central/hs/Auth/check_password",
                json={"Имя": data.username, "Пароль": data.password},
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
        if res.status_code == 200 and res.json().get("success"):
            await redis.delete(key)
            token = create_access_token({"sub": data.username})
            return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"1C error: {e}")

    await redis.incr(key)
    await redis.expire(key, BLOCK_SECONDS)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/protected")
async def protected(current_user: str = Depends(verify_token)):
    return {"message": f"Привіт, {current_user}"}
    

@app.get("/")
async def root():
    return {"message": "Hello Skarb"}


@app.get("/dogovorhistory/{client_id}")
async def get_data_from_external_api(client_id: str, authorization: str = Header(None)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/history/dogovorhistory/{client_id}"

    logger.bind(job="dogovorhistory").info("Received request for client_id: {client_id} with token: {authorization}",
                                          client_id=client_id, authorization=authorization)

    if authorization != f"Bearer {expected_token}":
        logger.bind(job="dogovorhistory").warning("Unauthorized access attempt with token: {authorization}", authorization=authorization)
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url, timeout=500.0)
            response.raise_for_status()

            logger.bind(job="dogovorhistory").info("Successful response for client_id: {client_id} with data: {data}",
                                                  client_id=client_id, data=response.json())

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="dogovorhistory").error("External API error for client_id: {client_id}. Status: {status_code}, Error: {error}",
                                                   client_id=client_id, status_code=e.response.status_code, error=str(e))
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="dogovorhistory").error("Request error for client_id: {client_id}. Error: {error}",
                                                   client_id=client_id, error=str(e))
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.get("/gettype/{search}/{category_id}", response_model=list[SType])
@cache(expire=240)
async def get_type_from_external_api(search: str, category_id: int, user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/gettype/{search}/{category_id}"

    logger.bind(job="gettype").info(
        "Received request for search: {search}, category_id: {category_id} by user: {user}",
        search=search,
        category_id=category_id,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url, timeout=10)
            response.raise_for_status()

            logger.bind(job="gettype").info(
                "Successful response for search: {search}, category_id: {category_id} with data: {data}",
                search=search,
                category_id=category_id,
                data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="gettype").error(
                "External API error for search: {search}, category_id: {category_id}. Status: {status_code}, Error: {error}",
                search=search,
                category_id=category_id,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="gettype").error(
                "Request error for search: {search}, category_id: {category_id}. Error: {error}",
                search=search,
                category_id=category_id,
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.get("/getvendor/{search}", response_model=list[SVendor])
@cache(expire=240)
async def get_vendor_from_external_api(search: str, user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/getvendor/{search}"

    logger.bind(job="get_vendor").info(
        "Received request for search: {search} by user: {user}",
        search=search,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(job="get_vendor").info(
                "Successful response for search: {search} with data: {data}",
                search=search,
                data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="get_vendor").error(
                "External API error for search: {search}. Status: {status_code}, Error: {error}",
                search=search,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="get_vendor").error(
                "Request error for search: {search}. Error: {error}",
                search=search,
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.post("/new_type")
async def get_data_from_external_api(data: dict, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/new_type/"
    headers = {"Content-Type": "application/json; charset=utf-8"}  # JSON формат передачі даних

    logger.bind(job="new_type").info(
        "Received request with data: {data} by user: {user}",
        data=data,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            json_data = json.dumps(data)
            logger.bind(job="new_type").debug("Sending data to external API: {json_data}", json_data=json_data)

            response = await client.post(central_base_api_url, data=json_data, headers=headers)
            response.raise_for_status()

            logger.bind(job="new_type").info(
                "Successful response from external API with data: {response_data}",
                response_data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="new_type").error(
                "External API error. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="new_type").error(
                "Request error while connecting to external API. Error: {error}",
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.post("/new_vendor")
async def get_data_from_external_api(data: dict, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/new_vendor/"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    logger.bind(job="new_vendor").info(
        "Received request for /new_vendor with data: {data} by user: {user}",
        data=data,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            json_data = json.dumps(data)
            logger.bind(job="new_vendor").debug("Sending data to external API: {json_data}", json_data=json_data)

            response = await client.post(central_base_api_url, data=json_data, headers=headers)
            response.raise_for_status()

            logger.bind(job="new_vendor").info(
                "Successful response from external API for /new_vendor with data: {response_data}",
                response_data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="new_vendor").error(
                "External API error for /new_vendor. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="new_vendor").error(
                "Request error while connecting to external API for /new_vendor. Error: {error}",
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, port=55335)
