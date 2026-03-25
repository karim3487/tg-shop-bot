from aiogram.enums import ParseMode
from pydantic import BaseModel, Field


class LogsConfig(BaseModel):
    level_name: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s [%(levelname)s] %(message)s")


class BotConfig(BaseModel):
    token: str = Field(...)
    parse_mode: ParseMode = Field(...)
    webapp_url: str = Field(default="http://localhost:3000")


class PostgresConfig(BaseModel):
    name: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    user: str = Field(...)
    password: str = Field(...)


class RedisConfig(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    database: int = Field(default=0)
    password: str | None = Field(None)


class CacheConfig(BaseModel):
    use_cache: bool = Field(default=False)


class MediaConfig(BaseModel):
    url: str = Field(default="http://localhost:9000/media")


class AppConfig(BaseModel):
    logs: LogsConfig
    bot: BotConfig
    postgres: PostgresConfig
    redis: RedisConfig
    cache: CacheConfig
    media: MediaConfig
