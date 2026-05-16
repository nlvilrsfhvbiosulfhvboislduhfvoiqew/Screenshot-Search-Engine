import os
from PIL import Image
import imagehash
from app.utils.logger import logger

def get_image_hash(image_path: str) -> str:
    """Calculates the perceptual hash of an image."""
    try:
        with Image.open(image_path) as img:
            return str(imagehash.phash(img))
    except Exception as e:
        logger.error(f"Failed to generate hash for {image_path}: {e}")
        return ""

def create_thumbnail(image_path: str, thumbnail_dir: str = "cache/thumbnails", size: tuple = (200, 200)) -> str:
    """Generates a thumbnail for the given image and returns the thumbnail path."""
    try:
        os.makedirs(thumbnail_dir, exist_ok=True)
        filename = os.path.basename(image_path)
        # To avoid collisions if filenames are same but in different folders
        # prefix with a hash of the original path
        safe_prefix = str(abs(hash(image_path)))
        thumb_filename = f"thumb_{safe_prefix}_{filename}"
        
        # Ensure it's saved as png or jpg to avoid webp issues in some Tkinter builds
        if not thumb_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            thumb_filename += '.jpg'
            
        thumb_path = os.path.join(thumbnail_dir, thumb_filename)
        
        if os.path.exists(thumb_path):
            return thumb_path

        with Image.open(image_path) as img:
            # Convert to RGB if it's RGBA or P to save as JPEG safely
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail(size)
            img.save(thumb_path, format="JPEG" if thumb_path.endswith(('.jpg', '.jpeg')) else "PNG")
            
        return thumb_path
    except Exception as e:
        logger.error(f"Failed to create thumbnail for {image_path}: {e}")
        return ""

def is_valid_image(file_path: str) -> bool:
    """Checks if a file is a valid image based on extension."""
    valid_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    ext = os.path.splitext(file_path)[1].lower()
    return ext in valid_extensions
