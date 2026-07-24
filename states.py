from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):

    waiting_full_name = State()

    waiting_phone = State()

    waiting_city = State()

    waiting_birth_date = State()

    waiting_receipt = State()


class Receipt(StatesGroup):

    waiting_receipt = State()