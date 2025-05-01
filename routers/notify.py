from fastapi import APIRouter, HTTPException
from datetime import datetime, time
from fastapi_cache import FastAPICache
from notifications.viber import send_viber
from notifications.sms import send_sms
from notifications.push import send_web_push, send_app_push
from notifications.templates import get_template
from routers.schema import NotificationRequest
import json

router = APIRouter(
    prefix='/notification',
    tags=['Send notification']
)

@router.post("/send_notification")
async def send_notification(data: NotificationRequest):
    redis = FastAPICache.get_backend().redis

    def should_delay(event_time: datetime) -> bool:
        local_time = event_time.astimezone().time()
        return local_time >= time(20, 0) or local_time < time(9, 0)

    if should_delay(data.event_time):
        key = f"delayed_notification:{data.client_id}"
        await redis.set(key, data.model_dump_json(), ex=86400)  # TTL на 1 добу
        return {"status": "scheduled", "client_id": data.client_id}

    try:
        await _send_now(data)
        return {"status": "sent", "client_id": data.client_id}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Template not found for status={data.status}, channel={data.channel}")


async def _send_now(data: NotificationRequest):
    tmpl = get_template(data.status, data.channel, data.name)
    msg = tmpl if isinstance(tmpl, str) else tmpl.get("text", "")

    payload = {
        "to": data.phone,
        "status": data.status,
        "channel": data.channel,
        "message": msg
    }

    if data.channel == "viber":
        await send_viber(data.phone, msg, data.client_id)
    elif data.channel == "sms":
        await send_sms(data.phone, msg, data.client_id)
    elif data.channel == "web_push":
        # print("[WEB PUSH]", json.dumps(payload, ensure_ascii=False))
        await send_web_push(
            uid=data.client_id,
            title=tmpl.get("title", ""),
            body=tmpl.get("text", msg),
            type_=tmpl.get("image", ""),
            link=tmpl.get("button_url", "https://www.skarb.com.ua/special"),
            message_text=msg
        )
    elif data.channel == "app_push":
        await send_app_push(phone=data.phone, text=msg, title=tmpl.get("title", ""))
    else:
        raise HTTPException(status_code=400, detail="Unknown channel")
