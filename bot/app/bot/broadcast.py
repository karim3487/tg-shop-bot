import asyncio
import logging
import os

import aiohttp
from aiogram import Bot
from aiogram.types import FSInputFile
from psycopg_pool import AsyncConnectionPool

from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
from app.infrastructure.database.db import DB

logger = logging.getLogger(__name__)

_INTERVAL = 30  # seconds between polls
_SEND_DELAY = 0.05  # 50ms between messages to avoid flood


async def _run_broadcast(bot: Bot, pool: AsyncConnectionPool, media_base_url: str) -> None:
    """Check for pending broadcasts and send them."""
    async with pool.connection() as raw_conn:
        db = DB(PsycopgConnection(raw_conn))
        pending = await db.broadcasts.get_pending()

    for broadcast in pending:
        logger.info("Starting broadcast #%s", broadcast.id)

        # Mark as sending in a separate connection
        async with pool.connection() as raw_conn:
            db = DB(PsycopgConnection(raw_conn))
            await db.broadcasts.set_sending(broadcast_id=broadcast.id)

        # Get all recipients
        async with pool.connection() as raw_conn:
            db = DB(PsycopgConnection(raw_conn))
            telegram_ids = await db.clients.get_all_active_telegram_ids()

        sent = 0
        errors = 0
        image_file: FSInputFile | None = None

        if broadcast.image and media_base_url:
            # Download image to tmp cache for reuse
            img_path = f"/tmp/broadcast_{broadcast.id}.jpg"
            
            # Helper to check if file exists and write it
            def _save_image(path, content):
                with open(path, "wb") as f:
                    f.write(content)

            file_exists = await asyncio.to_thread(os.path.exists, img_path)
            if not file_exists:
                try:
                    url = f"{media_base_url.rstrip('/')}/{broadcast.image}"
                    timeout = aiohttp.ClientTimeout(total=15)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=timeout) as resp:
                            if resp.status == 200:
                                content = await resp.read()
                                await asyncio.to_thread(_save_image, img_path, content)
                except Exception as e:
                    logger.warning("Failed to download broadcast image: %s", e)
            
            if await asyncio.to_thread(os.path.exists, img_path):
                image_file = FSInputFile(img_path)

        for telegram_id in telegram_ids:
            try:
                if image_file:
                    await bot.send_photo(
                        chat_id=telegram_id,
                        photo=image_file,
                        caption=broadcast.text,
                    )
                else:
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=broadcast.text,
                    )
                sent += 1
            except Exception as e:
                logger.debug("Failed to send to %s: %s", telegram_id, e)
                errors += 1
            await asyncio.sleep(_SEND_DELAY)

        async with pool.connection() as raw_conn:
            db = DB(PsycopgConnection(raw_conn))
            await db.broadcasts.finish(
                broadcast_id=broadcast.id,
                sent_count=sent,
                error_count=errors,
            )

        logger.info(
            "Broadcast #%s done: %s sent, %s errors",
            broadcast.id, sent, errors,
        )


async def broadcast_worker(bot: Bot, pool: AsyncConnectionPool, media_base_url: str) -> None:
    """Background loop that polls for ready broadcasts."""
    logger.info("Broadcast worker started (interval=%ss)", _INTERVAL)
    while True:
        try:
            await _run_broadcast(bot, pool, media_base_url)
        except Exception as e:
            logger.exception("Broadcast worker error: %s", e)
        await asyncio.sleep(_INTERVAL)
