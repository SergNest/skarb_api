from pydantic import BaseModel


class ImageData(BaseModel):
    filename: str
    image_base64: str

