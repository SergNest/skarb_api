from fastapi import APIRouter, UploadFile, HTTPException
from photo import read_imagefile, compare_images

router = APIRouter(
    prefix='/photo',
    tags=['work with photo']
)


@router.post("/unique_images")
async def filter_unique_images(files: list[UploadFile]):
    try:
        images = [(file.filename, read_imagefile(await file.read())) for file in files]
        unique_images = []

        for filename, img in images:
            if not any(compare_images(img, comp_img) for _, comp_img in unique_images):
                unique_images.append((filename, img))

        return len(unique_images)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")