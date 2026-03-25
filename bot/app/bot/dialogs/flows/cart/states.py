from aiogram.fsm.state import State, StatesGroup


class CartSG(StatesGroup):
    cart = State()
    item_manage = State()
