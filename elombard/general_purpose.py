import httpx

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from typing import Optional, List

from auth import authenticate
from elombard.schema import AddPhoneSchema, SPhonePS, DataSchema, SBonus
from conf.config import settings
from utils.logger_config import logger

router = APIRouter(
    prefix='/general',
    tags=['General purpose']
)


@router.get("/get_phone_ps/{search}", response_model=List[SPhonePS])
@cache(expire=1800)
async def get_phone_ps(search: str, user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/get_phone_ps/{search}"

    logger.bind(job="get_phone_ps").info(
        "Received request for search: {search} by user: {user}",
        search=search,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(job="get_phone_ps").info(
                "Successful response for search: {search} with data: {data}",
                search=search,
                data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="get_phone_ps").error(
                "External API error for search: {search}. Status: {status_code}, Error: {error}",
                search=search,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="get_phone_ps").error(
                "Request error for search: {search}. Error: {error}",
                search=search,
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@router.get("/get_phone_all", response_model=DataSchema)
@cache(expire=1800)
async def get_phone(user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/get_phone"

    logger.bind(job="get_phone").info(
         "Received request by user: {user}",
        user=user
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(job="get_phone").info(
                "Successful response for data: {data}",
                data=response.json()
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="get_phone").error(
                "External API error. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="get_phone").error(
                "Request error. Error: {error}",
                error=str(e)
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@router.post("/add_phone", response_model=DataSchema)
async def add_phone(phone_data: AddPhoneSchema, user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/add_phone"
    
    logger.bind(job="add_phone").info(
        "Received request to add phone: {phone_data} by user: {user}",
        phone_data=phone_data.dict(),
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(central_base_api_url, json=phone_data.dict())
            response.raise_for_status()

            logger.bind(job="add_phone").info(
                "Successful addition of phone: {phone_data}",
                phone_data=phone_data.dict()
            )
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="add_phone").error(
                "External API error while adding phone. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError as e:
            logger.bind(job="add_phone").error(
                "Request error while adding phone. Error: {error}",
                error=str(e)
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@router.get("/getbonus/{client_cod}/{date}", response_model=SBonus)
@cache(expire=60)
async def get_vendor_from_external_api(client_cod: str, date: str, user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/get_bonus/{client_cod}/{date}"

    logger.bind(job="get_bonus").info(
        "Received request for search: {client_cod} by date: {date}",
        client_cod=client_cod,
        date=date,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(job="get_bonus").info(
                "Successful response for search: {client_cod} with data: {date}",
                client_cod=client_cod,
                date=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="get_bonus").error(
                "External API error for search: {client_cod}. Status: {status_code}, Error: {error}",
                client_cod=client_cod,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail=f"External API returned {str(e)}")
        except httpx.RequestError as e:
            logger.bind(job="get_bonus").error(
                "Request error for search: {client_cod}. Error: {error}",
                client_cod=client_cod,
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")