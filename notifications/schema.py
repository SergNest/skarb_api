from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SMassage(BaseModel):
    lo_address: str
    chat_id: Optional[int] = -4076579827
    movement: Optional[str] = 'buy'
    val: Optional[str] = 'USD'
    val_sum: int = 50
    val_national_sum: float = 2007.5
    course: float = 40.15

