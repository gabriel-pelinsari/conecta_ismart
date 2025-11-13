from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "ISMART_CONECTA"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Database - pode usar DATABASE_URL direto (Supabase) ou campos individuais
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === EMAIL CONFIG ===
    EMAIL_SENDER: str = "seu-email@gmail.com"
    EMAIL_APP_PASSWORD: str = "sua-senha-app"

    # === ADMIN CONFIG ===
    ADMIN_VERIFICATION_CODE: str = "ADMIN123456"

    def get_database_url(self) -> str:
        """Retorna DATABASE_URL se fornecida, caso contrário monta a partir dos campos"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        extra = "allow"  # Permite campos extras no .env

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()