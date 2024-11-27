import httpx

from fastapi import APIRouter, HTTPException, Depends


from auth import authenticate
from conf.config import settings
from typing import Optional


from sun_flower.schema import DelayRequest, SuccessResponse, ErrorResponse

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
    data: DelayRequest,
    user: Optional[str] = Depends(authenticate)
):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/sf/new_delay/"

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    async with httpx.AsyncClient() as client:
        try:
            json_data = [item.dict() for item in data.items]
            response = await client.post(central_base_api_url, json=json_data, headers=headers)
            response.raise_for_status()

            return SuccessResponse(
                status="success",
                data=response.json()
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



