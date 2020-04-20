#import image
from PIL import Image
import pytesseract

def scan_file(file):
    text = pytesseract.image_to_string(Image.open(file))
    return text

#print(scan_file('scantron-100.jpg'))