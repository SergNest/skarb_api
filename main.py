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

from auth import authenticate, expected_token
from conf.config import settings
from src.schema import SType, SVendor

from elombard.zok import router as zok
from elombard.new_offer import router as offer
from notifications.telegram_send import router as telegram_send
from work_with_foto.photo_route import router as photo
from sun_flower.sunflower_route import router as sf
from utils.logger_config import logger


BLOCKED_PATHS = ["/.env", "/.git", "/.config", "/config.json", "/sslvpn_logon.shtml"]

app = FastAPI()


@app.middleware("http")
async def block_paths_middleware(request: Request, call_next):
    if request.url.path in BLOCKED_PATHS:
        logger.warning(f"Blocked access to {request.url.path} from {request.client.host}")
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


@app.get("/")
async def root():
    return {"message": "Hello Skarb"}


@app.get("/dogovorhistory/{client_id}")
async def get_data_from_external_api(client_id: str, authorization: str = Header(None)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/history/dogovorhistory/{client_id}"

    logger.bind(dogovorhistory=True).info("Received request for client_id: {client_id} with token: {authorization}",
                                          client_id=client_id, authorization=authorization)

    if authorization != f"Bearer {expected_token}":
        logger.bind(dogovorhistory=True).warning("Unauthorized access attempt with token: {authorization}", authorization=authorization)
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url, timeout=500.0)
            response.raise_for_status()

            logger.bind(dogovorhistory=True).info("Successful response for client_id: {client_id} with data: {data}",
                                                  client_id=client_id, data=response.json())

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(dogovorhistory=True).error("External API error for client_id: {client_id}. Status: {status_code}, Error: {error}",
                                                   client_id=client_id, status_code=e.response.status_code, error=str(e))
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(dogovorhistory=True).error("Request error for client_id: {client_id}. Error: {error}",
                                                   client_id=client_id, error=str(e))
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.get("/gettype/{search}/{category_id}", response_model=list[SType])
@cache(expire=240)
async def get_type_from_external_api(search: str, category_id: int, user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/gettype/{search}/{category_id}"

    logger.bind(gettype=True).info(
        "Received request for search: {search}, category_id: {category_id} by user: {user}",
        search=search,
        category_id=category_id,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(gettype=True).info(
                "Successful response for search: {search}, category_id: {category_id} with data: {data}",
                search=search,
                category_id=category_id,
                data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(gettype=True).error(
                "External API error for search: {search}, category_id: {category_id}. Status: {status_code}, Error: {error}",
                search=search,
                category_id=category_id,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(gettype=True).error(
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

    logger.bind(get_vendor=True).info(
        "Received request for search: {search} by user: {user}",
        search=search,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(get_vendor=True).info(
                "Successful response for search: {search} with data: {data}",
                search=search,
                data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(get_vendor=True).error(
                "External API error for search: {search}. Status: {status_code}, Error: {error}",
                search=search,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(get_vendor=True).error(
                "Request error for search: {search}. Error: {error}",
                search=search,
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.post("/new_type")
async def get_data_from_external_api(data: dict, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/new_type/"
    headers = {"Content-Type": "application/json; charset=utf-8"}  # JSON формат передачі даних

    logger.bind(new_type=True).info(
        "Received request with data: {data} by user: {user}",
        data=data,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            json_data = json.dumps(data)
            logger.bind(new_type=True).debug("Sending data to external API: {json_data}", json_data=json_data)

            response = await client.post(central_base_api_url, data=json_data, headers=headers)
            response.raise_for_status()

            logger.bind(new_type=True).info(
                "Successful response from external API with data: {response_data}",
                response_data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(new_type=True).error(
                "External API error. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(new_type=True).error(
                "Request error while connecting to external API. Error: {error}",
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.post("/new_vendor")
async def get_data_from_external_api(data: dict, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/new_vendor/"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    logger.bind(new_vendor=True).info(
        "Received request for /new_vendor with data: {data} by user: {user}",
        data=data,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            json_data = json.dumps(data)
            logger.bind(new_vendor=True).debug("Sending data to external API: {json_data}", json_data=json_data)

            response = await client.post(central_base_api_url, data=json_data, headers=headers)
            response.raise_for_status()

            logger.bind(new_vendor=True).info(
                "Successful response from external API for /new_vendor with data: {response_data}",
                response_data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(new_vendor=True).error(
                "External API error for /new_vendor. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(new_vendor=True).error(
                "Request error while connecting to external API for /new_vendor. Error: {error}",
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, port=55335)
