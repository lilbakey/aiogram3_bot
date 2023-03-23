from aiogram.filters import BaseFilter
from aiogram.types import Message

from models.Category import Category


class CheckNameCategory(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        name = await Category.check_name_in_base(message.text)
        return True if name else False
