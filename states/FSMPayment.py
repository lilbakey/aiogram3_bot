from aiogram.fsm.state import StatesGroup, State


class FSMPayment(StatesGroup):
    total_amount: State = State()
    accept: State = State()