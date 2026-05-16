import os
import cv2
import pytesseract
import numpy as np
from PIL import Image

from app.utils.logger import logger

class OCREngine:
    def __init__(self, tesseract_cmd: str = None):
        """
        Initializes the OCR Engine. 
        If tesseract_cmd is provided, it configures pytesseract to use it.
        Otherwise, it assumes tesseract is in the system PATH.
        """
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Default common installation paths for Windows
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
            ]
            for path in common_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocesses the image to improve OCR accuracy.
        - Converts to grayscale
        - Applies thresholding
        - Noise reduction
        """
        try:
            # Read image using OpenCV
            # We use numpy fromfile to handle unicode paths in Windows
            stream = open(image_path, "rb")
            bytes = bytearray(stream.read())
            numpyarray = np.asarray(bytes, dtype=np.uint8)
            img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
            stream.close()

            if img is None:
                raise ValueError("Could not decode image.")

            # Convert to RGB if it has alpha channel
            if len(img.shape) == 3 and img.shape[2] == 4:
                # Create a white background image
                alpha_channel = img[:, :, 3]
                rgb_channels = img[:, :, :3]
                white_background_image = np.ones_like(rgb_channels, dtype=np.uint8) * 255
                # Apply the alpha channel
                alpha_factor = alpha_channel[:, :, np.newaxis] / 255.0
                alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)
                base = rgb_channels * alpha_factor
                white = white_background_image * (1 - alpha_factor)
                img = (base + white).astype(np.uint8)

            # Convert to grayscale
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img

            # Rescale image to 300 DPI equivalent if small (heuristics)
            height, width = gray.shape
            if width < 1000:
                gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            # Apply Otsu's thresholding
            # For screenshots with text, adaptive thresholding can also work, but simple binary 
            # with Otsu is usually good for sharp contrast like text on screen.
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            return thresh

        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return None

    def extract_text(self, image_path: str, lang: str = 'eng') -> str:
        """
        Extracts text from the image using Tesseract OCR.
        """
        try:
            processed_img = self.preprocess_image(image_path)
            
            if processed_img is not None:
                # Convert back to PIL Image for pytesseract
                pil_img = Image.fromarray(processed_img)
                # Configuration:
                # --psm 3: Fully automatic page segmentation, but no OSD. (Default)
                # --oem 3: Default, based on what is available.
                custom_config = r'--oem 3 --psm 3'
                text = pytesseract.image_to_string(pil_img, lang=lang, config=custom_config)
            else:
                # Fallback to direct PIL read if preprocessing fails
                text = pytesseract.image_to_string(Image.open(image_path), lang=lang)
                
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract not found. Please ensure it is installed and in PATH.")
            return "[OCR ERROR: Tesseract Not Found]"
        except Exception as e:
            logger.error(f"Failed to extract text from {image_path}: {e}")
            return ""
