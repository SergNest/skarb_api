from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SType(BaseModel):
    name: str
    guid: str
    id: int
    group_id: int


class SVendor(BaseModel):
    name: str
    guid: str
    id: int


