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

settings = Settings()
