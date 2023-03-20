from aiogram.fsm.state import StatesGroup, State


class FSMSettings(StatesGroup):
    help: State = State()
    faq: State = State()
    photo: State = State()