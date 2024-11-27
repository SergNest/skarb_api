from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DelayRequestItem(BaseModel):
    Timestamp: str = Field(..., description="Timestamp of the delay")
    client_uuid: str = Field(..., description="UUID of the client")
    comment: Optional[str] = Field(None, description="Additional information about the delay")
    manager: Optional[str] = Field(None, description="Manager responsible for the request")
    pawnshop: Optional[str] = Field(None, description="Identifier of the pawnshop")


class DelayRequest(BaseModel):
    items: List[DelayRequestItem] = Field(..., description="List of delay requests")


class SuccessResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    data: Optional[dict] = Field(None, description="Additional data for the response")


class ErrorResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    error: str = Field(..., description="Error message")
