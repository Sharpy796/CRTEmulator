import cv2
from PIL import Image
import numpy as np
import matplotlib as plt
import os

for image_path in os.listdir('assets\gif'):
    with Image.open('assets/gif/'+image_path) as im:
        im.seek(5)
        im.save('assets/png/{}.png'.format(image_path))

# This might be ported to another language.