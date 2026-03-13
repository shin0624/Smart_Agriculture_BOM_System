
import os
import shutil
from PIL import Image
from DB.database import ASSETS_PARTS_PATH

THUMB_SIZE = (300, 300)

def save_part_image(src_path: str, part_id: int) -> str:
    """이미지를 assets/parts/{part_id}.jpg 로 저장 후 경로 반환"""
    os.makedirs(ASSETS_PARTS_PATH, exist_ok=True)
    dest = os.path.join(ASSETS_PARTS_PATH, f"{part_id}.jpg")
    try:
        img = Image.open(src_path).convert("RGB")
        img.thumbnail(THUMB_SIZE, Image.LANCZOS)
        img.save(dest, "JPEG", quality=85)
    except Exception:
        shutil.copy2(src_path, dest)
    return dest

def get_part_image_path(part_id: int) -> str | None:
    path = os.path.join(ASSETS_PARTS_PATH, f"{part_id}.jpg")
    return path if os.path.exists(path) else None


def delete_part_image(image_path: str | None) -> bool:
    if not image_path:
        return False
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            return True
    except Exception:
        return False
    return False
