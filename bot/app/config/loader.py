from app.config.models import (
    AppConfig,
    BotConfig,
    CacheConfig,
    LogsConfig,
    MediaConfig,
    PostgresConfig,
    RedisConfig,
)
from app.config.settings import settings

_s = settings


def get_config() -> AppConfig:
    return AppConfig(
        logs=LogsConfig(
            level_name=_s.logs.level_name,
            format=_s.logs.format,
        ),
        bot=BotConfig(
            token=_s.bot_token,
            parse_mode=_s.bot.parse_mode,
            webapp_url=_s.bot.get("webapp_url", "http://localhost:3000"),
        ),
        postgres=PostgresConfig(
            name=_s.postgres.name,
            host=_s.postgres.host,
            port=_s.postgres.port,
            user=_s.postgres.user,
            password=_s.postgres_password,
        ),
        redis=RedisConfig(
            host=_s.redis.host,
            port=_s.redis.port,
            database=_s.redis.database,
            password=_s.get("redis_password", None),
        ),
        cache=CacheConfig(use_cache=_s.cache.use_cache),
        media=MediaConfig(url=_s.get("media.url", "http://localhost:9000/media")),
    )
