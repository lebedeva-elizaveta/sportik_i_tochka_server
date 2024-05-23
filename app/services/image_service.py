import os
import uuid
from PIL import Image
from flask import url_for

from app.config import AppConfig


class ImageService:
    @staticmethod
    def save_image(file, upload_folder):
        image_processor = ImageProcessor(file, upload_folder)
        return image_processor.save()

    @staticmethod
    def get_static_file_url(file_path, folder):
        file_url = StaticFileUrlBuilder(file_path, folder)
        return file_url.build()

    @staticmethod
    def get_uploaded_file_url(file_path, folder):
        file_url = UploadedFileUrlBuilder(file_path, folder)
        return file_url.build()


class ImageProcessor:
    def __init__(self, file, upload_folder):
        self.file = file
        self.upload_folder = upload_folder

    def save(self):
        self.file.seek(0, os.SEEK_END)
        file_size = self.file.tell()
        self.file.seek(0)

        if file_size > AppConfig.MAX_CONTENT_LENGTH:
            raise ValueError("Size is too large")

        image = Image.open(self.file)
        if image.format not in AppConfig.ALLOWED_EXTENSIONS:
            raise ValueError("Invalid extension")
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        unique_filename = str(uuid.uuid4()) + '.jpg'
        processed_file_path = os.path.join(self.upload_folder, unique_filename)
        image.save(processed_file_path, "JPEG", optimize=True, quality=75)
        return processed_file_path


class FileUrlBuilder:
    def __init__(self, file_path, folder):
        self.file_path = file_path
        self.folder = folder

    def build(self):
        if self.file_path is None:
            return None
        filename = os.path.basename(self.file_path)
        return self.build_url(filename)

    def build_url(self, filename):
        raise NotImplementedError("Subclasses should implement this method")


class StaticFileUrlBuilder(FileUrlBuilder):
    def build_url(self, filename):
        return url_for('static', filename=f"{self.folder}/{filename}")


class UploadedFileUrlBuilder(FileUrlBuilder):
    def build_url(self, filename):
        return url_for('file_bp.uploaded_file', folder=self.folder, filename=filename)
