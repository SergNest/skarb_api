import httpx

from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from typing import Optional

from auth import authenticate
from elombard.schema import SZok, SBonusWithdraw
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

    logger.bind(job="check_zok_by_phone").info(
        "Received request for /check_zok_by_phone with phone: {phone}, date: {date}, user: {user}",
        phone=phone,
        date=date,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url, timeout=15)
            response.raise_for_status()

            logger.bind(job="check_zok_by_phone").info(
                "External API responded successfully for /check_zok_by_phone with data: {response_data}",
                response_data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="check_zok_by_phone").error(
                "External API error for /check_zok_by_phone. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="External API returned error",
            )
        except httpx.RequestError as e:
            logger.bind(job="check_zok_by_phone").error(
                "Request error while connecting to external API for /check_zok_by_phone. Error: {error}",
                error=str(e),
            )
            raise HTTPException(
                status_code=500,
                detail="Error connecting to external API",
            )


@router.get("/checkmoneyBonusWithdraw/{client_id}", response_model=SBonusWithdraw)
@cache(expire=3600)
async def get_bonus_withdraw(client_id: str, user: Optional[str] = Depends(authenticate)):

    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/checkmoneyBonusWithdraw/{client_id}"

    logger.bind(job="get_bonus_withdraw").info(
        "Received request for /get_bonus_withdraw with client_id: {client_id}, user: {user}",
        client_id=client_id, user=user)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()

            logger.bind(job="get_bonus_withdraw").info(
                "External API responded successfully for /get_bonus_withdraw with data: {response_data}",
                response_data=response.json(),
            )

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.bind(job="get_bonus_withdraw").error(
                "External API error for /get_bonus_withdraw. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="External API returned error",
            )
        except httpx.RequestError as e:
            logger.bind(job="get_bonus_withdraw").error(
                "Request error while connecting to external API for /get_bonus_withdraw. Error: {error}",
                error=str(e),
            )
            raise HTTPException(
                status_code=500,
                detail="Error connecting to external API",
            )