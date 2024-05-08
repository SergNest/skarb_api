from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SZok(BaseModel):
    Error: bool
    TextError: str
    InZok: bool | None = None
    ZokDate: Optional[datetime] = None
