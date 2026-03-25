from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.tables.bot_settings import BotSettingsTable
from app.infrastructure.database.tables.broadcasts import BroadcastsTable
from app.infrastructure.database.tables.cart import CartTable
from app.infrastructure.database.tables.catalog import CatalogTable
from app.infrastructure.database.tables.clients import ClientsTable
from app.infrastructure.database.tables.faq import FAQTable
from app.infrastructure.database.tables.orders import OrdersTable


class DB:
    def __init__(self, connection: BaseConnection) -> None:
        self.clients = ClientsTable(connection=connection)
        self.catalog = CatalogTable(connection=connection)
        self.cart = CartTable(connection=connection)
        self.orders = OrdersTable(connection=connection)
        self.faq = FAQTable(connection=connection)
        self.settings = BotSettingsTable(connection=connection)
        self.broadcasts = BroadcastsTable(connection=connection)
