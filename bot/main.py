import asyncio

from app.bot.bot import main as start_bot
from app.config.loader import get_config
from app.config.models import AppConfig
from app.infrastructure.log_setup import setup_logging


async def main() -> None:
    config: AppConfig = get_config()

    setup_logging(config=config)

    await start_bot(config=config)


asyncio.run(main())
