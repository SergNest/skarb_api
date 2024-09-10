from pydantic import BaseModel, HttpUrl
from typing import List


class ImageData(BaseModel):
    filename: str
    image_base64: str


class ImageUrls(BaseModel):
    urls: List[HttpUrl]  # Список URL з перевіркою, що це коректний формат URL