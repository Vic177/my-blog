import os
import PIL
from PIL import Image
import uuid
from flask import current_app, request, url_for, redirect, flash
from . import photosSet

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

# 裁剪相册图片
def resize_image(image, filename, base_width):
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] <= base_width:
        return filename + ext
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    filename += current_app.config['FLASKY_PHOTO_SUFFIX'][base_width] + ext
    img.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename), optimize=True, quality=85)
    return filename

