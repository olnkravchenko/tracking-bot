import xml.dom as dom
from os import listdir
from dominate import document
from dominate.tags import *

imagesPath = './images/qr_codes/'
images = listdir(imagesPath)

with document(title='QRcodes2HTML') as doc:
    for path in images:
        tr(img(src=imagesPath+path))

with open('qr_codes.html', 'w') as file:
    file.write(doc.render())
