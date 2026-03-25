import asyncio
import logging

import psycopg_pool
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from aiogram_dialog import setup_dialogs

from app.bot.broadcast import broadcast_worker
from app.bot.dialogs import all_dialogs
from app.bot.handlers import routers
from app.bot.middlewares.database import DataBaseMiddleware
from app.bot.middlewares.get_user import GetUserMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.subscription import SubscriptionMiddleware
from app.bot.order_notifier import order_notifier_worker
from app.config.models import AppConfig
from app.infrastructure.database.connection.connect_to_pg import get_pg_pool

logger = logging.getLogger(__name__)



async def setup_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="catalog", description="Открыть каталог"),
        BotCommand(command="cart", description="Корзина"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)


async def main(config: AppConfig) -> None:
    logger.info("Starting bot")

    redis_url = (
        f"redis://:{config.redis.password}@"
        f"{config.redis.host}:{config.redis.port}/{config.redis.database}"
    )
    storage = RedisStorage.from_url(redis_url, key_builder=DefaultKeyBuilder(with_destiny=True))

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode(config.bot.parse_mode)),
    )
    dp = Dispatcher(storage=storage)

    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.postgres.name,
        host=config.postgres.host,
        port=config.postgres.port,
        user=config.postgres.user,
        password=config.postgres.password,
    )

    # Inject shared data into all handlers/getters
    dp.workflow_data.update(
        db_pool=db_pool,
        redis=storage.redis,
        media_base_url=config.media.url,
        webapp_url=config.bot.webapp_url,
    )

    # Middlewares (order matters: DB → GetUser → ShadowBan → Subscription)
    dp.update.middleware(DataBaseMiddleware())
    dp.update.middleware(GetUserMiddleware())
    dp.update.middleware(ShadowBanMiddleware())
    dp.update.middleware(SubscriptionMiddleware())

    dp.errors.middleware(DataBaseMiddleware())
    dp.errors.middleware(GetUserMiddleware())

    # Regular routers (commands, faq inline, errors)
    for router in routers:
        dp.include_router(router)

    # Dialog routers
    for dialog in all_dialogs:
        dp.include_router(dialog)

    # Setup aiogram-dialog (must be called after all routers are included)
    setup_dialogs(dp)

    logger.info("Setting chat menu button for WebApp...")
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Магазин",
            web_app=WebAppInfo(url=config.bot.webapp_url)
        )
    )

    logger.info("Setting bot commands...")
    await setup_commands(bot)

    logger.info("Bot started, polling...")
    broadcast_task = asyncio.create_task(
        broadcast_worker(bot, db_pool, config.media.url)
    )
    notifier_task = asyncio.create_task(
        order_notifier_worker(bot, db_pool, config)
    )
    try:
        await dp.start_polling(bot)
    finally:
        broadcast_task.cancel()
        notifier_task.cancel()
        await db_pool.close()
        await storage.close()
        logger.info("Bot stopped")
