import httpx

from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from typing import Optional

from auth import authenticate
from elombard.schema import SZok
from conf.config import settings


router = APIRouter(
    prefix='/zok',
    tags=['Clients ZOK']
)


@router.get("/check_zok_by_phone", response_model=SZok)
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