from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DelayRequest(BaseModel):
    client_uuid: str = Field(..., description="Uuid of the client")
    comment: str = Field(..., description="Additional information about the delay")
    # delay_date: datetime = Field(..., description="The date and time of the delay in format 'YYYY-MM-DD HH:MM:SS'")
    manager: Optional[str] = Field(None, description="Manager responsible for the request")
    pawnshop: Optional[str] = Field(None, description="Identifier of the pawnshop")


    # class Config:
    #     anystr_strip_whitespace = True
    #     json_encoders = {
    #         datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
    #     }


class SuccessResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    data: Optional[dict] = Field(None, description="Additional data for the response")

class ErrorResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    error: str = Field(..., description="Error message")