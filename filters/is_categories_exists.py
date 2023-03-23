from aiogram.filters import BaseFilter
from aiogram.types import Message

from models.Category import Category


class IsCategoriesExists(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        categories = await Category.get_all()
        return True if categories else False
