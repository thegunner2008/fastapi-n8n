import os
from typing import ClassVar

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Settings(BaseSettings):
    PROJECT_NAME: ClassVar[str] = os.getenv('PROJECT_NAME', 'FASTAPI BASE')
    SECRET_KEY: ClassVar[str] = os.getenv('SECRET_KEY', '')
    API_PREFIX: ClassVar[str] = ''
    BACKEND_CORS_ORIGINS: ClassVar[str] = ['*']
    DATABASE_URL: ClassVar[str] = os.getenv('SQL_DATABASE_URL', '')
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # Token expired after 7 days
    SECURITY_ALGORITHM: ClassVar[str] = 'HS256'
    LOGGING_CONFIG_FILE: ClassVar[str] = os.path.join(BASE_DIR, 'logging.ini')


settings = Settings()
