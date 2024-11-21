from pydantic import BaseModel, Field
from typing import List, Optional


class DelayRequest(BaseModel):
    Client_uuid: str = Field(..., description="Uuid of the client")
    Comment: str = Field(..., description="Additional information about the delay")
    Manager: Optional[str] = Field(None, description="Manager responsible for the request")
    Pawnshop: Optional[str] = Field(None, description="Identifier of the pawnshop")

class SuccessResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    data: Optional[dict] = Field(None, description="Additional data for the response")

class ErrorResponse(BaseModel):
    status: str = Field(..., description="Status of the request")
    error: str = Field(..., description="Error message")