from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "OBE Paper Analysis System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",
    ]

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./obe_analysis.db"
    # 如果需要PostgreSQL，使用以下格式：
    # DATABASE_URL: str = "postgresql://user:password@localhost/obe_analysis"

    # AI API配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()