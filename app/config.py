from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/inventory"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
