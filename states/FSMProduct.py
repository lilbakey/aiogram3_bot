from aiogram.fsm.state import StatesGroup, State


class FSMProduct(StatesGroup):
    download_photo: State = State()
    download_name: State = State()
    download_description: State = State()
    download_price: State = State()
    download_category: State = State()
    delete_product: State = State()
    delete_step: State = State()
    product_id: State = State()