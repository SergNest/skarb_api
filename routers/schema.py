from datetime import datetime
from pydantic import BaseModel, validator

class NotificationRequest(BaseModel):
    client_id: str
    name: str
    status: str  # "silver" or "gold"
    channel: str  # "web_push" | "app_push" | "viber" | "sms"
    phone: str
    event_time: datetime

    @validator('event_time', pre=True)
    def parse_event_time(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
            except ValueError:
                raise ValueError(
                    "The 'event_time' field must be in the format 'dd.mm.yyyy HH:MM:SS', for example: '05.05.2025 15:56:55'."
                )
        elif isinstance(value, datetime):
            return value
        raise TypeError("Invalid type for 'event_time'. Expected string or datetime.")