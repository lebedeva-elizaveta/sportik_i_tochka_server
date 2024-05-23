from flask import Blueprint, jsonify, send_from_directory, current_app
import os

file_bp = Blueprint('file_bp', __name__)


@file_bp.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    valid_folders = ['activities', 'avatars']
    if folder not in valid_folders:
        return jsonify({"error": "Invalid folder"}), 400

    folder_path = os.path.join(current_app.root_path, 'uploads', folder)
    return send_from_directory(folder_path, filename)
