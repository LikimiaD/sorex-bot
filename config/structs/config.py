import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    TELEGRAM_TOKEN: str = Field(alias="TELEBOT_TOKEN")
    MAX_WORKERS: int = Field(alias="API_MAX_WORKERS")
    COINMARKET_API_KEY: str = Field(alias="COINMARKET_API")
    CHANNEL_ID: int = Field(alias="TELEBOT_STATS_CHANNEL")
    DB_NAME: str = Field(alias="DB_NAME")
    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: int = Field(alias="DB_PORT")
    DB_USER: str = Field(alias="DB_USER")
    DB_PASSWORD: str = Field(alias="DB_PASSWORD")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '..', ".env")

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


if __name__ == "__main__":
    cfg: Config = Config()
    print(cfg.model_dump())
