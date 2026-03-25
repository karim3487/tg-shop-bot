from aiogram.fsm.state import State, StatesGroup


class OrderSG(StatesGroup):
    full_name = State()
    address = State()
    confirm = State()
    payment = State()  # stub payment + "Я оплатил(а)"
