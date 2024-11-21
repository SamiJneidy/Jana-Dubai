from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class Settings(BaseSettings):
    database_hostname: str
    database_name: str
    database_port: int
    database_username: str
    database_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    password_reset_token_expire_minutes: int
    mail_username: str
    mail_password: str
    mail_from: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()