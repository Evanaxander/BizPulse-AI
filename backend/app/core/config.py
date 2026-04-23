from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    groq_api_key: str
    openai_api_key: str
    secret_key: str

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()