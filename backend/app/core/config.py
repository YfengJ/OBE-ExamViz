from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "OBE Paper Analysis System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"

    DATABASE_URL: str = "sqlite:///./obe_analysis.db"
    AUTO_SEED_DEMO_DATA: bool = False

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    SECRET_KEY: str = "replace-with-random-secret"
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.ALLOWED_ORIGINS.split(",") if item.strip()]


settings = Settings()
