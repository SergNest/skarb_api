from fastapi import APIRouter, UploadFile, HTTPException, Depends

from auth import authenticate
from photo import read_imagefile, compare_images, decode_base64_image, load_image_from_url
from work_with_foto.schema import ImageData, ImageUrls
from typing import List, Optional

router = APIRouter(
    prefix='/photo',
    tags=['work with photo']
)


@router.post("/unique_images_base64")
async def filter_unique_images(files: list[ImageData], user: Optional[str] = Depends(authenticate)):
    try:
        # Декодуємо зображення з base64 і зберігаємо їх разом з іменами
        images = [(file.filename, decode_base64_image(file.image_base64)) for file in files]
        unique_images = []

        for filename, img in images:
            # Перевіряємо, чи зображення унікальне
            if not any(compare_images(img, comp_img) for _, comp_img in unique_images):
                unique_images.append((filename, img))

        return {"unique_count": len(unique_images), "unique_filenames": [filename for filename, _ in unique_images]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/unique_images_from_urls")
async def filter_unique_images_from_urls(data: ImageUrls, user: Optional[str] = Depends(authenticate)):
    try:
        images = [(url, load_image_from_url(url)) for url in data.urls]
        unique_images = []

        for url, img in images:
            if not any(compare_images(img, comp_img) for _, comp_img in unique_images):
                unique_images.append((url, img))

        return {"unique_count": len(unique_images), "unique_urls": [url for url, _ in unique_images]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/unique_images")
async def filter_unique_images(files: list[UploadFile], user: Optional[str] = Depends(authenticate)):
    try:
        images = [(file.filename, read_imagefile(await file.read())) for file in files]
        unique_images = []

        for filename, img in images:
            if not any(compare_images(img, comp_img) for _, comp_img in unique_images):
                unique_images.append((filename, img))

        return len(unique_images)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")



