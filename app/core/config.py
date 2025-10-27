import os

from pydantic import ConfigDict, PostgresDsn, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


load_dotenv()


class DatabaseSettings(BaseModel):
    """Class DatabaseSettings."""

    model_config = ConfigDict(extra="ignore")

    host: str = os.environ.get("DB_HOSTNAME", "localhost")
    port: int = int(os.environ.get("DB_PORT", "5432"))
    username: str = os.environ.get("DB_USERNAME", "postgres")
    password: str = os.environ.get("DB_PASSWORD", "password")
    database: str = os.environ.get("DB_NAME", "padel_tournaments")

    @property
    def dsn(self) -> str:
        """Builds Postgres DSN."""
        # Allow override with DATABASE_DSN environment variable
        custom_dsn = os.environ.get("DATABASE_DSN")
        if custom_dsn:
            return custom_dsn
            
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.database,
            )
        )
    
class Settings(BaseSettings):
    # Database
    db: DatabaseSettings = DatabaseSettings()
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = ""  # Optional - will be generated dynamically
    
    # Frontend URL
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    
    # CORS Settings
    @property
    def allowed_origins(self) -> list[str]:
        """Get allowed CORS origins based on environment."""
        if self.DEBUG:
            return ["*"]  # Allow all origins in development
        return [self.FRONTEND_URL]
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # General Settings
    DEBUG: bool = os.environ.get("DEBUG", "true").lower() == "true"
    
    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_file_encoding="utf-8",
        env_file=".env",
        extra="ignore",
    )


settings = Settings() 