from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = ""
    PORT: int = 8000
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    CLOUDINARY_NAME: str = ""
    CLOUDINARY_API_KEY: int = 0
    CLOUDINARY_API_SECRET: str = ""

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 465
    MAIL_SERVER: str = ""
    MAIL_FROM_NAME: str = ""

    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )  # type: ignore


settings = Settings()  # type: ignore
