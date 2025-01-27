import httpx
from fastapi import APIRouter, HTTPException, Depends
from auth import authenticate
from conf.config import settings
from typing import Optional

from elombard.schema import OfferSuccessResponse, OfferErrorResponse, OfferRequest
from utils.logger_config import logger

router = APIRouter(
    prefix='/offer',
    tags=['work with offers']
)


@router.post(
    "/new_offer",
    response_model=OfferSuccessResponse,
    responses={
        400: {"model": OfferErrorResponse, "description": "Bad Request"},
        500: {"model": OfferErrorResponse, "description": "Internal Server Error"},
    },
)
async def create_new_offer(
    request_data: OfferRequest,
    user: Optional[str] = Depends(authenticate),
):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/new_offer/"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    logger.bind(job="new_offer").info(
        "Received request for /new_offer with data: {data} by user: {user}",
        data=request_data.dict(),
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(central_base_api_url, json=request_data.dict(), headers=headers, timeout=20)
            response.raise_for_status()

            logger.bind(job="new_offer").info(
                "External API responded successfully for /new_offer with data: {response_data}",
                response_data=response.json(),
            )

            return OfferSuccessResponse(
                status="success",
                data=response.json(),
            )
        except httpx.HTTPStatusError as e:
            logger.bind(job="new_offer").error(
                "External API error for /new_offer. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="External API returned error",
            )
        except httpx.RequestError as e:
            logger.bind(job="new_offer").error(
                "Request error while connecting to external API for /new_offer. Error: {error}",
                error=str(e),
            )
            raise HTTPException(
                status_code=500,
                detail="Error connecting to external API",
            )
