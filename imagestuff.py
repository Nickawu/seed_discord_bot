import subprocess
from PIL import Image
import pytesseract

imgtext = subprocess.check_output(["tesseract","IMG-3536.jpg","stdout",'-l "eng"'])
print(imgtext)
img = Image.open('IMG-3534.jpg')
pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
text = pytesseract.image_to_string('IMG-3534.jpg')
print(text)

# import json

# test_dict = {
#     "Owenry Magruder" : ['NotFred310','owen','notfred'],
#     "H0pe" : ['Armo','Xilent'],
#     "Shaay" : ['Adena', 'Fussi']
# }

# f = open("nickname_dict.txt", "w+")
# f.write(json.dumps(test_dict))