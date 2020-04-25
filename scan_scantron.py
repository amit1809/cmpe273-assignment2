#import image
import json
from PIL import Image
#import pytesseract

def scan_jpeg_file(file):
    text = pytesseract.image_to_string(Image.open(file))
    return text

def scan_json_file(file):
    with open(file, "r") as fp:
        scantron_dict = json.load(fp)
    return scantron_dict
#print(scan_file('scantron-100.jpg'))