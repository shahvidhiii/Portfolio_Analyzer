import os
import pytesseract

os.environ['TESSDATA_PREFIX'] = r"C:\PROGRA~1\Tesseract-OCR\tessdata"
pytesseract.pytesseract.tesseract_cmd = r"C:\PROGRA~1\Tesseract-OCR\tesseract.exe"

from PIL import Image
import numpy as np
import cv2
import pytesseract
import shutil
from pytesseract import TesseractError, Output, image_to_data


def _deskew_image(gray):
    coords = np.column_stack(np.where(gray > 0))
    if len(coords) < 10:
        return gray
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def preprocess_image(pil_image, scale=2, denoise=True, deskew=True):
    """Return a preprocessed grayscale OpenCV image ready for OCR."""
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if denoise:
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
    # adaptive threshold for varied lighting
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 11, 2)

    if deskew:
        th = _deskew_image(th)

    # enlarge to improve OCR recognition
    h, w = th.shape
    th = cv2.resize(th, (max(1, w*scale), max(1, h*scale)), interpolation=cv2.INTER_LINEAR)

    # optional morphological opening to clean small noise
    kernel = np.ones((1, 1), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    return th


def ocr_image(pil_image, psm=6, oem=1, lang='eng', preprocess=True, return_image=False):
    if preprocess:
        th = preprocess_image(pil_image)
    else:
        th = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2GRAY)

    config = f"--psm {psm} --oem {oem}"

    text = pytesseract.image_to_string(th, lang=lang, config=config)

    if return_image:
        return text, Image.fromarray(th)
    return text
