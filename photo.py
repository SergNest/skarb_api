from PIL import Image
import cv2
import numpy as np
from io import BytesIO
import base64

# Функція для порівняння зображень на основі ORB
def compare_images(img1, img2):
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)
    threshold = 220  # Порогова кількість ключових точок
    return len(matches) > threshold


# Функція для конвертації зображень у формат, який можна порівнювати через ORB
def read_imagefile(file) -> np.array:
    image = Image.open(BytesIO(file))
    image = np.array(image.convert('RGB'))  # Конвертуємо у формат RGB
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


# Функція для декодування base64 у зображення
def decode_base64_image(image_base64: str):
    image_data = base64.b64decode(image_base64)
    # Перетворюємо байти у numpy array
    np_arr = np.frombuffer(image_data, np.uint8)
    # Читаємо зображення з numpy array
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Error decoding image")
    return img