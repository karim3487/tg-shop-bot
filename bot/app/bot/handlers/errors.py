import logging

from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)

errors_router = Router()


@errors_router.errors()
async def handle_error(event: ErrorEvent) -> None:
    logger.exception("Unhandled error: %s", event.exception, exc_info=event.exception)
