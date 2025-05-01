from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseSettings):

    bot_token: str = os.getenv('BOT_TOKEN', 'BOT_TOKEN')

    expected_token: str = os.getenv('EXPECTED_TOKEN', 'EXPECTED_TOKEN')
    ip_central: str = os.getenv('IP_CENTRAL', 'IP_CENTRAL')
    port_central: str = os.getenv('PORT_CENTRAL', 'PORT_CENTRAL')

    redis_ip: str = os.getenv('REDIS_IP', 'REDIS_IP')
    redis_port: str = os.getenv('REDIS_PORT', 'REDIS_PORT')
    secret_key: str = os.getenv('SECRET_KEY', 'SECRET_KEY')
    
    
    secret: str = os.getenv('SECRET', 'SECRET')
    point: str = os.getenv('POINT', 'POINT')    
    elombard: str = os.getenv('ELOMBARD', 'ELOMBARD')

    homenkoPushURL: str = os.getenv('HOMENKOURL', 'HOMENKOURL') 
    homenkoBearer: str = os.getenv('HOMENKOBEARER', 'HOMENKOBEARER') 

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf8'


settings = Settings()
