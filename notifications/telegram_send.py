import httpx

from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from fastapi_cache.decorator import cache

from bot import send_notification
from notifications.schema import SMassage
from conf.config import settings

emoji_dict = {
    "buy": "🟢 куплено",
    "sell": "🔴 продано",
    "dollar": "🇺🇸",
    "euro": "🇪🇺"
}

expected_token = settings.expected_token
security = HTTPBearer()

router = APIRouter(
    prefix='/telegram',
    tags=['send to telega']
)


@router.post("/")
async def send_to_group(body: SMassage):
    try:
        # Формування повідомлення з використанням даних з об'єкта SMassage
        message = (
            f" {body.lo_address}\n"
            f" {emoji_dict.get(body.movement)}\n"
            f"Val: {emoji_dict.get(body.val)}\n"
            f"Сума валюти: {body.val_sum}\n"
            f"Сума гривні: {body.val_national_sum}\n"
            f"Курс: {body.course}\n"
        )
        await send_notification(body.chat_id, message)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="Error connecting to external API")

