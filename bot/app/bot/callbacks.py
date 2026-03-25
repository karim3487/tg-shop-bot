from aiogram.filters.callback_data import CallbackData


class CheckSubscriptionCallback(CallbackData, prefix="check_sub"):
    pass


class OrderActionCallback(CallbackData, prefix="order_action"):
    order_id: int
    action: str  # new status: pending|paid|processing|shipped|delivered|cancelled


class CatCB(CallbackData, prefix="cat"):
    id: int


class CatPageCB(CallbackData, prefix="cat_page"):
    id: int
    page: int


class ProdCB(CallbackData, prefix="prod"):
    id: int


class CartAddCB(CallbackData, prefix="cart_add"):
    product_id: int


class CartItemCB(CallbackData, prefix="ci"):
    action: str  # up | down | rm
    item_id: int
