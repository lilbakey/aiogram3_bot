from aiogram.types import Message
from aiogram.filters import BaseFilter
from config_data.config import Config, load_config


config: Config = load_config('.env')

admins_id: list[int] = config.tg_bot.admins_id


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admins_id


