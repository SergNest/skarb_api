import httpx

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from typing import Optional

from auth import authenticate
from elombard.schema import SPhonePS
from conf.config import settings
from utils.logger_config import logger

router = APIRouter(
    prefix='/general',
    tags=['General purpose']
)


@router.get("/get_phone_ps/{search}", response_model=SPhonePS)
@cache(expire=3600)
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