from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SMassage(BaseModel):
    lo_address: str
    chat_id: Optional[int] = -4076579827
    movement: Optional[str] = 'buy'
    val: Optional[str] = 'dollar'
    val_sum: int
    val_national_sum: int
    course: float

