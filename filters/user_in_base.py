from aiogram.types import Message
from aiogram.filters import BaseFilter

from models.User import User


class UserInBase(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await User.check_user_in_base(int(message.from_user.id))
