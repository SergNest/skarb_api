from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseSettings):

    expected_token: str = os.getenv('EXPECTED_TOKEN', 'EXPECTED_TOKEN')
    ip_central: str = os.getenv('IP_CENTRAL', 'IP_CENTRAL')
    port_central: str = os.getenv('PORT_CENTRAL', 'PORT_CENTRAL')

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf8'


settings = Settings()
