import asyncio
import json
import sys
import os
from datetime import datetime
from redis import asyncio as aioredis

# Додаємо корінь проекту до sys.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routers.notify import _send_now, NotificationRequest
from conf.config import settings  # Використовуємо той самий settings

async def process_all():
    redis_url = f"redis://{settings.redis_ip}:{settings.redis_port}"
    redis = await aioredis.from_url(redis_url, decode_responses=True)
    keys = await redis.keys("delayed_notification:*")

    print(f"[INFO] Found {len(keys)} delayed notifications")

    for key in keys:
        try:
            raw = await redis.get(key)
            data = NotificationRequest.model_validate_json(raw)
            await _send_now(data)
            await redis.delete(key)
            print(f"[SENT] To {data.client_id} at {datetime.now().isoformat()}")
        except Exception as e:
            print(f"[ERROR] Failed to send for {key}: {e}")

if __name__ == "__main__":
    asyncio.run(process_all())
