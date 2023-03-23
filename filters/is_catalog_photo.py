from aiogram.types import CallbackQuery, Message

from models.CatalogPhoto import CatalogPhoto
from aiogram.filters import BaseFilter


class IsCatalogPhoto(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        photo: str = await CatalogPhoto.get_photo()
        return True if photo else False
