import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    secret_key: str = os.getenv('SECRET_KEY')
    aes_key: bytes = bytes.fromhex(os.getenv('AES_KEY'))
    aes_iv: bytes = bytes.fromhex(os.getenv('AES_IV'))


class AppConfig:
    ALGORITHM = "HS256"
    ALLOWED_EXTENSIONS = {'PNG', 'JPG', 'JPEG'}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    FOLDER_ACTIVITIES = 'app/uploads/activities/'
    FOLDER_ACHIEVEMENTS = 'app/static/achievements/'
    FOLDER_AVATARS = 'app/uploads/avatars/'

    upload_folders = [
        FOLDER_ACTIVITIES,
        FOLDER_AVATARS,
    ]

    def __init__(self):
        self.settings = Settings()

    @staticmethod
    def create_upload_folders():
        for folder in AppConfig.upload_folders:
            os.makedirs(folder, exist_ok=True)


app_config = AppConfig()
app_config.create_upload_folders()
settings = Settings()
