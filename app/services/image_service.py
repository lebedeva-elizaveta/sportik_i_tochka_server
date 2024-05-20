import os
import uuid

from PIL import Image
from flask import url_for

from app.config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH


def save_image(file, upload_folder):

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_CONTENT_LENGTH:
        raise ValueError("Size is too large")

    image = Image.open(file)
    if image.format not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid extension")
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    unique_filename = str(uuid.uuid4()) + '.jpg'
    processed_file_path = os.path.join(upload_folder, unique_filename)
    image.save(processed_file_path, "JPEG", optimize=True, quality=75)
    return processed_file_path


def uploaded_file(file_path, folder):
    filename = os.path.basename(file_path)
    return url_for('static', filename=f"{folder}/{filename}")

