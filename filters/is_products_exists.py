from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from models.Product import Product
from models.Category import Category


class IsProductsExists(BaseFilter):

    async def __call__(self, callback: CallbackQuery) -> bool:
        category_name: str = callback.data.split(': ')[1]
        category_id: str = await Category.get_category_id(category_name)
        list_of_products: list[dict[str, Union[str, int]]] = await Product.get_products_in_category(category_id)

        return True if list_of_products else False
