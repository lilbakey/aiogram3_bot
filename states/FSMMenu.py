from aiogram.fsm.state import StatesGroup, State


class FSMMenu(StatesGroup):
    step: State = State()
    category: State = State()
    product_id: State = State()
