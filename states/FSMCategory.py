from aiogram.fsm.state import StatesGroup, State


class FSMCategory(StatesGroup):
    download_category: State = State()
    delete_category: State = State()