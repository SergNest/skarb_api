from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field


class SZok(BaseModel):
    Error: bool
    TextError: str
    InZok: bool | None = None
    ZokDate: Optional[datetime] = None


class OfferRequest(BaseModel):
    phone: str = Field(..., description="Phone number of the client 380932223344")
    segment: int = Field(..., description="Segment feature")
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


class SOfferErrorResponseXMl(BaseModel):
    status: str = Field(..., description="Status of the request")
    error: str = Field(..., description="Error message")


class SOfferRequestXMl(BaseModel):
    TypeRequest: Optional[str] = "LidOffer"
    tel: Optional[str]
    tip: Optional[str]
    vid: Optional[str]
    UID: Optional[str]
    srok: Optional[str]
    hint_short: Optional[str]
    hint_long: Optional[str]
    SMS: Optional[str]
    otpravitel: Optional[str]
    actionType: Optional[str]
    rowId: Optional[str]


class SPhonePS(BaseModel):
    tech: str | None = None
    gold: str | None = None


# Опис внутрішньої моделі для телефону
class PhoneInfo(BaseModel):
    gold: str
    tech: str


# Опис основної моделі, де ключі – рядки, а значення – PhoneInfo
class DataSchema(BaseModel):
    __root__: Dict[str, PhoneInfo]
