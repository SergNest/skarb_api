import httpx

from fastapi import APIRouter, HTTPException, Depends
from auth import authenticate
from conf.config import settings
from typing import Optional, List
from datetime import datetime
from utils.logger_config import logger
# from loguru import logger

from sun_flower.schema import DelayRequestItem, SuccessResponse, ErrorResponse

# logger.remove()
# logger.add("app.log", rotation="10 MB", retention="10 days", compression="zip")

router = APIRouter(
    prefix='/sf',
    tags=['sun flower']
)


@router.post(
    "/new_delay",
    response_model=SuccessResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def set_delay_from_external_api(
    data: List[DelayRequestItem],  # Приймає список об'єктів
    user: Optional[str] = Depends(authenticate),
):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/sf/new_delay/"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    logger.bind(new_delay=True).info(
        "Received request for /new_delay with data: {data} by user: {user}",
        data=data,
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            # Перетворення Timestamp у кожному елементі
            converted_data = []
            for item in data:
                try:
                    timestamp = datetime.strptime(item.Timestamp, "%Y-%m-%d %H:%M:%S.%f")  # Розбір вхідного формату
                    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Форматування до потрібного
                except ValueError as e:
                    logger.bind(new_delay=True).error(
                        "Timestamp conversion error for item: {item}. Error: {error}",
                        item=item.dict(),
                        error=str(e),
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid timestamp format: {e}",
                    )

                converted_item = item.dict()
                converted_item["Timestamp"] = formatted_timestamp
                converted_data.append(converted_item)

            logger.bind(new_delay=True).info(
                "Converted data for /new_delay: {converted_data}",
                converted_data=converted_data,
            )

            response = await client.post(central_base_api_url, json=converted_data, headers=headers)
            response.raise_for_status()

            logger.bind(new_delay=True).info(
                "External API responded successfully for /new_delay with data: {response_data}",
                response_data=response.json(),
            )

            return SuccessResponse(
                status="success",
                data=response.json(),
            )
        except httpx.HTTPStatusError as e:
            logger.bind(new_delay=True).error(
                "External API error for /new_delay. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="External API returned error",
            )
        except httpx.RequestError as e:
            logger.bind(new_delay=True).error(
                "Request error while connecting to external API for /new_delay. Error: {error}",
                error=str(e),
            )
            raise HTTPException(
                status_code=500,
                detail="Error connecting to external API",
            )



