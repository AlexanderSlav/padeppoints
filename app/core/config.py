import os

from pydantic import ConfigDict, PostgresDsn, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


load_dotenv()


class DatabaseSettings(BaseModel):
    """Class DatabaseSettings."""

    model_config = ConfigDict(extra="ignore")

    host: str = os.environ["DB_HOSTNAME"]
    port: int = os.environ["DB_PORT"]
    username: str = os.environ["DB_USERNAME"]
    password: str = os.environ["DB_PASSWORD"]
    database: str = os.environ["DB_NAME"]

    @property
    def dsn(self) -> str:
        """Builds Postgres DSN."""
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
    APP_NAME: str
    DEBUG: bool
    
    # Database
    db: DatabaseSettings = DatabaseSettings()
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_file_encoding="utf-8",
        env_file=".env",
        extra="ignore",
    )


settings = Settings() 