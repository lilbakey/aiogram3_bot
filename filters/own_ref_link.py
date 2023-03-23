from aiogram.filters import BaseFilter
from aiogram.types import Message


class OwnRefLink(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        referrer_id: str = str(message.text[7:])
        return referrer_id == str(message.from_user.id)
