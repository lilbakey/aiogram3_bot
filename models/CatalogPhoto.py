from models.data_base import async_db_session, BaseModel
from models.AdminModel import AdminModel

from sqlalchemy import (Column, Integer, String)
from sqlalchemy import (select, delete as sqlalchemy_delete)
from sqlalchemy.orm import Mapped


class CatalogPhoto(BaseModel, AdminModel):
    __tablename__: str = 'catalog_photos'

    id: Mapped[int] = Column(Integer, primary_key=True)

    photo: Mapped[String] = Column(String, nullable=False)

    @classmethod
    async def get_photo(cls) -> str:
        query = select(cls.photo)
        photo = await async_db_session.execute(query)
        photo = photo.scalars().first()

        return photo

    @classmethod
    async def delete_photo(cls) -> None:
        query = sqlalchemy_delete(cls)
        await async_db_session.execute(query)

        try:
            await async_db_session.commit()
        except Exception:
            await async_db_session.rollback()
            raise
