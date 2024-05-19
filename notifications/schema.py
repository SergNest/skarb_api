from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SMassage(BaseModel):
    lo_address: int
    chat_id: int
    movement: str
    val: str
    val_sum: int
    val_national_sum: int
    course: float

