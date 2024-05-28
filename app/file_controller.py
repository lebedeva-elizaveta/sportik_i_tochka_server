from flask import Blueprint, send_from_directory
import os

from app.exceptions.exceptions import NotFoundException

file_bp = Blueprint('file_bp', __name__)


@file_bp.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    root_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_folder = os.path.join(root_folder, 'uploads', folder)
    full_file_path = os.path.join(image_folder, filename)
    if not os.path.exists(full_file_path):
        raise NotFoundException("File not found")
    return send_from_directory(image_folder, filename)
