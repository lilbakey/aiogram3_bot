from aiogram.types import Message

from models.FAQ import FAQ
from aiogram.filters import BaseFilter


class IsFAQContent(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        help_content: str = await FAQ.get_faq_content()
        return True if help_content else False