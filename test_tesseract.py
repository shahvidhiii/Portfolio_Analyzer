from PIL import Image
from ocr_utils import ocr_image

img = Image.new("RGB", (300, 100), "white")
print(ocr_image(img))
