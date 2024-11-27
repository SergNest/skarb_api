import httpx

from fastapi import APIRouter, HTTPException, Depends
from auth import authenticate
from conf.config import settings
from typing import Optional, List
from datetime import datetime

from sun_flower.schema import DelayRequestItem, SuccessResponse, ErrorResponse

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
    user: Optional[str] = Depends(authenticate)
):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/sf/new_delay/"

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    async with httpx.AsyncClient() as client:
        try:
            # Перетворення Timestamp у кожному елементі
            converted_data = []
            for item in data:
                # Конвертація Timestamp до необхідного формату
                timestamp = datetime.strptime(item.Timestamp, "%Y-%m-%d %H:%M:%S.%f")  # Розбір вхідного формату
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Форматування до потрібного

                # Додати до списку змінені об'єкти
                converted_item = item.dict()
                converted_item["Timestamp"] = formatted_timestamp
                converted_data.append(converted_item)

            # Відправлення даних
            response = await client.post(central_base_api_url, json=converted_data, headers=headers)
            response.raise_for_status()

            return SuccessResponse(
                status="success",
                data=response.json()
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timestamp format: {e}"
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail="External API returned error"
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=500,
                detail="Error connecting to external API"
            )



