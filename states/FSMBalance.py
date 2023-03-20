from aiogram.fsm.state import StatesGroup, State

class FSMBalance(StatesGroup):
    replenish_balance: State = State()
    user: State = State()