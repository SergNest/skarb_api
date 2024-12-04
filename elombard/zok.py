import httpx

from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from typing import Optional

from auth import authenticate
from elombard.schema import SZok
from conf.config import settings
from utils.logger_config import logger

router = APIRouter(
    prefix='/zok',
    tags=['Clients ZOK']
)


@router.get("/check_zok_by_phone", response_model=SZok)
@cache(expire=3600)
async def get_zok_by_phone(
    phone: str,
    date: Optional[datetime] = None,
    user: Optional[str] = Depends(authenticate),
):
    central_base_api_url = (
        f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/checkzokbyphone"
        f"?phone={phone}&date={date}"
    )

    logger.bind(check_zok_by_phone=True).info(
        "Received request for /check_zok_by_phone with phone: {phone}, date: {date}, user: {user}",
        phone=phone,
        date=date,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(check_zok_by_phone=True).info(
                "External API responded successfully for /check_zok_by_phone with data: {response_data}",
                response_data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(check_zok_by_phone=True).error(
                "External API error for /check_zok_by_phone. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="External API returned error",
            )
        except httpx.RequestError as e:
            logger.bind(check_zok_by_phone=True).error(
                "Request error while connecting to external API for /check_zok_by_phone. Error: {error}",
                error=str(e),
            )
            raise HTTPException(
                status_code=500,
                detail="Error connecting to external API",
            )
