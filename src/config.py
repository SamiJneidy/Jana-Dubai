from pydantic_settings import BaseSettings, SettingsConfigDict

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
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()