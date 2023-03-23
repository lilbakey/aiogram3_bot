from aiogram.types import Message

from models.Help import Help
from aiogram.filters import BaseFilter


class IsHelpContent(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        help_content: str = await Help.get_help_content()
        return True if help_content else False
