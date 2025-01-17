from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SZok(BaseModel):
    Error: bool
    TextError: str
    InZok: bool | None = None
    ZokDate: Optional[datetime] = None


class OfferRequest(BaseModel):
    phone: str = Field(..., description="Phone number of the client +380932223344")
    offer: Optional[str] = Field(None, description="Optional offer details")


class OfferSuccessResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    data: Optional[dict] = Field(None, description="Additional data for the response")


class OfferErrorResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    error: str = Field(..., description="Error message")


class SBonusWithdraw(BaseModel):
    Iid: str
    Lo: str
    Org: str
    last_zok_org: str
    Phone: str
    Error: str

