from aiogram.filters import BaseFilter
from aiogram.types import Message

from models import Basket, Product


class IsBasketExist(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        basket: Basket = await Basket.get_basket(telegram_id=int(message.from_user.id))
        products: list = [await Product.get_object(i.product_id) for i in basket.products]
        list_of_products: list[tuple[str, str | int]] = [(i.name, i.price) for i in products]

        print('*' * 50)
        print(list_of_products)

        return True if list_of_products else False
