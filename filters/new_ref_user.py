from aiogram.types import Message
from aiogram.filters import BaseFilter


class NewRefUser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        referrer_id: str = str(message.text[7:])
        return referrer_id and referrer_id != str(message.from_user.id)
