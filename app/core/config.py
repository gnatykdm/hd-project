from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class ConfigSettings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Point to your .env file relative to this script
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings: ConfigSettings = ConfigSettings()
