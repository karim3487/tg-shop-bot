from app.bot.handlers.admin import admin_router
from app.bot.handlers.commands import commands_router
from app.bot.handlers.errors import errors_router
from app.bot.handlers.faq import faq_router

__all__ = ["routers"]

routers = [
    admin_router,
    commands_router,
    faq_router,
    errors_router,
]
