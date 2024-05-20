import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    secret_key: str = os.getenv('SECRET_KEY')
    aes_key: bytes = bytes.fromhex(os.getenv('AES_KEY'))
    aes_iv: bytes = bytes.fromhex(os.getenv('AES_IV'))


ALGORITHM = "HS256"
FOLDER_ACTIVITIES = 'app/static/images/activities/'
FOLDER_ACHIEVEMENTS = 'app/static/images/achievements/'
FOLDER_AVATARS = 'app/static/images/avatars/'
ALLOWED_EXTENSIONS = {'PNG', 'JPG', 'JPEG'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

settings = Settings()
