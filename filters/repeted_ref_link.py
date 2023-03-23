from aiogram.filters import BaseFilter
from aiogram.types import Message


class RepeatedRefLink(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        referrer_id: str = str(message.text[7:])
        return True if referrer_id else False
