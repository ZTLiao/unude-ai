from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "UnudeAI Clone"
    secret_key: str = "dev-secret"
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite:///./app.db"
    media_dir: str = str(BASE_DIR / "media")

    default_provider: str = "pollinations"
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    pollinations_image_url: str = "https://image.pollinations.ai/prompt"
    pollinations_text_url: str = "https://text.pollinations.ai/openai"

    register_bonus_credits: int = 100

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
