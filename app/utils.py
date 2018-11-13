import os
import PIL
from PIL import Image
import uuid
from flask import current_app
from . import photosSet

"""
def resize_image(image, filename, base_width):
	filename, ext = os.path.splitext(filename)
	image = Image.open(image)
	if image.size[0] < base_width:
		return filename + ext
	w_percent = (base_width / float(image.size[0]))
	h_size = int((float(image.size[1]) * float(w_percent)))

	img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

	filename += current_app.config['FLASKY_PHOTO_SUFFIX'][base_width] + ext
	image.save(os.path.join(current_app.config['PHOTO_SAVE_PATH'], filename), optimize=True, quality=85)

	return filename
"""

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