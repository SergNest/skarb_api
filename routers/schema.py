from datetime import datetime
from pydantic import BaseModel

class NotificationRequest(BaseModel):
    client_id: str
    name: str
    status: str  # "silver" або "gold"
    channel: str  # "web_push" | "app_push" | "viber" | "sms"
    phone: str
    event_time: datetime