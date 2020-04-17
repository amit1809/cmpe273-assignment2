#import image
from PIL import Image
import pytesseract

def scan_scantron(file):
    text = pytesseract.image_to_string(Image.open(file))
    return text

print(scan_scantron('scantron-100.jpg'))