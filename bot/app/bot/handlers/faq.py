import logging

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from app.infrastructure.database.db import DB

logger = logging.getLogger(__name__)

faq_router = Router()


@faq_router.inline_query()
async def inline_faq(query: InlineQuery, db: DB) -> None:
    search = query.query.strip()

    if search:
        items = await db.faq.search(query=search)
    else:
        items = await db.faq.get_all()

    if not items:
        await query.answer(
            results=[],
            switch_pm_text="Вопросы не найдены",
            switch_pm_parameter="faq",
            cache_time=10,
        )
        return

    results = [
        InlineQueryResultArticle(
            id=str(item.id),
            title=item.question,
            description=item.answer[:100],
            input_message_content=InputTextMessageContent(
                message_text=f"❓ <b>{item.question}</b>\n\n{item.answer}",
                parse_mode="HTML",
            ),
        )
        for item in items
    ]

    await query.answer(results=results, cache_time=30)
