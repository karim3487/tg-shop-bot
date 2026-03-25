from app.bot.dialogs.flows.cart.dialogs import cart_dialog
from app.bot.dialogs.flows.catalog.dialogs import catalog_dialog
from app.bot.dialogs.flows.main.dialogs import main_dialog
from app.bot.dialogs.flows.order.dialogs import order_dialog

all_dialogs = [
    main_dialog,
    catalog_dialog,
    cart_dialog,
    order_dialog,
]
